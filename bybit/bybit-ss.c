/*
 * lws-bybit
 *
 * Written in 2010-2021 by Andy Green <andy@warmcat.com>
 *                         Kutoga <kutoga@user.github.invalid>
 *
 * This file is made available under the Creative Commons CC0 1.0
 * Universal Public Domain Dedication.
 *
 * This demonstrates a Secure Streams implementation of a client that connects
 * to binance ws server efficiently.
 *
 * Build lws with -DLWS_WITH_SECURE_STREAMS=1 -DLWS_WITHOUT_EXTENSIONS=0
 *
 * "policy.json" contains all the information about endpoints, protocols and
 * connection validation, tagged by streamtype name.
 *
 * The example tries to load it from the cwd, it lives
 * in ./minimal-examples/secure-streams/minimal-secure-streams-binance dir, so
 * either run it from there, or copy the policy.json to your cwd.  It's also
 * possible to put the policy json in the code as a string and pass that at
 * context creation time.
 */

#include <libwebsockets.h>
#include <string.h>
#include <signal.h>
#include <ctype.h>

extern int test_result;

typedef struct range {
	uint64_t		sum;
	uint64_t		lowest;
	uint64_t		highest;

	unsigned int		samples;
} range_t;

LWS_SS_USER_TYPEDEF
	lws_sorted_usec_list_t	sul_hz;	     /* 1hz summary dump */

	range_t			e_lat_range;
	range_t			price_range;

	char			msg[64];
	const char		*payload;
	size_t			size;
	size_t			pos;

	int			count;
} bybit_t;


static void
range_reset(range_t *r)
{
	r->sum = r->highest = 0;
	r->lowest = 999999999999ull;
	r->samples = 0;
}

static uint64_t
get_us_timeofday(void)
{
	struct timeval tv;

	gettimeofday(&tv, NULL);

	return (uint64_t)((lws_usec_t)tv.tv_sec * LWS_US_PER_SEC) +
			  (uint64_t)tv.tv_usec;
}

static uint64_t
pennies(const char *s)
{
	uint64_t price = (uint64_t)atoll(s) * 100;

	s = strchr(s, '.');

	if (s && isdigit(s[1]) && isdigit(s[2]))
		price = price + (uint64_t)((10 * (s[1] - '0')) + (s[2] - '0'));

	return price;
}

static void
sul_hz_cb(lws_sorted_usec_list_t *sul)
{
	bybit_t *bin = lws_container_of(sul, bybit_t, sul_hz);
	bybit_t *g = bin;

	// /* provide a hint about the payload size */
	g->pos = 0;
	g->payload = g->msg;
	g->size = (size_t)lws_snprintf(g->msg, sizeof(g->msg),
					"{\"op\": \"subscribe\", \"args\": [\"orderBookL2_25.BTCUSD\"]}");

	if (lws_ss_request_tx_len(lws_ss_from_user(g), (unsigned long)g->size))
		lwsl_notice("%s: req failed\n", __func__);

	/*
	 * We are called once a second to dump statistics on the connection
	 */

	lws_sul_schedule(lws_ss_get_context(bin->ss), 0, &bin->sul_hz,
			 sul_hz_cb, LWS_US_PER_SEC);

	if (bin->price_range.samples)
		lwsl_ss_user(lws_ss_from_user(bin),
			    "price: min: %llu¢, max: %llu¢, avg: %llu¢, "
			    "(%d prices/s)",
			    (unsigned long long)bin->price_range.lowest,
			    (unsigned long long)bin->price_range.highest,
			    (unsigned long long)(bin->price_range.sum /
						    bin->price_range.samples),
			    bin->price_range.samples);
	if (bin->e_lat_range.samples)
		lwsl_ss_user(lws_ss_from_user(bin),
			    "elatency: min: %llums, max: %llums, "
			    "avg: %llums, (%d msg/s)",
			    (unsigned long long)bin->e_lat_range.lowest / 1000,
			    (unsigned long long)bin->e_lat_range.highest / 1000,
			    (unsigned long long)(bin->e_lat_range.sum /
					   bin->e_lat_range.samples) / 1000,
			    bin->e_lat_range.samples);

	range_reset(&bin->e_lat_range);
	range_reset(&bin->price_range);

	test_result = 0;
}

static lws_ss_state_return_t
bybit_transfer_callback(void *userobj, lws_ss_tx_ordinal_t ord, uint8_t *buf, size_t *len,
	     int *flags)
{
	bybit_t *bin = (bybit_t *)userobj;
	lws_ss_state_return_t r = LWSSSSRET_OK;
	bybit_t *g = bin;

	lwsl_user("bybit_transfer_callback");

	if (g->size == g->pos)
		return LWSSSSRET_TX_DONT_SEND;

	if (*len > g->size - g->pos)
		*len = g->size - g->pos;

	if (!g->pos)
		*flags |= LWSSS_FLAG_SOM;

	memcpy(buf, g->payload + g->pos, *len);
	g->pos += *len;

	if (g->pos != g->size)
		/* more to do */
		r = lws_ss_request_tx(lws_ss_from_user(g));
	else
		*flags |= LWSSS_FLAG_EOM;

	lwsl_ss_user(lws_ss_from_user(g), "TX %zu, flags 0x%x, r %d", *len,
					  (unsigned int)*flags, (int)r);

	return r;
}


static lws_ss_state_return_t
bybit_receive_callback(void *userobj, const uint8_t *in, size_t len, int flags)
{
	bybit_t *bin = (bybit_t *)userobj;
	uint64_t latency_us, now_us;
	char numbuf[16];
	uint64_t price;
	const char *p;
	size_t alen;

	lwsl_user("bybit_receive_callback %s", in);
	now_us = (uint64_t)get_us_timeofday();

	p = lws_json_simple_find((const char *)in, len, "\"depthUpdate\"",
				 &alen);
	if (!p)
		return LWSSSSRET_OK;

	p = lws_json_simple_find((const char *)in, len, "\"E\":", &alen);
	if (!p) {
		lwsl_err("%s: no E JSON\n", __func__);
		return LWSSSSRET_OK;
	}

	lws_strnncpy(numbuf, p, alen, sizeof(numbuf));
	latency_us = now_us - ((uint64_t)atoll(numbuf) * LWS_US_PER_MS);

	if (latency_us < bin->e_lat_range.lowest)
		bin->e_lat_range.lowest = latency_us;
	if (latency_us > bin->e_lat_range.highest)
		bin->e_lat_range.highest = latency_us;

	bin->e_lat_range.sum += latency_us;
	bin->e_lat_range.samples++;

	p = lws_json_simple_find((const char *)in, len, "\"a\":[[\"", &alen);
	if (!p)
		return LWSSSSRET_OK;

	lws_strnncpy(numbuf, p, alen, sizeof(numbuf));
	price = pennies(numbuf);

	if (price < bin->price_range.lowest)
		bin->price_range.lowest = price;
	if (price > bin->price_range.highest)
		bin->price_range.highest = price;

	bin->price_range.sum += price;
	bin->price_range.samples++;

	return LWSSSSRET_OK;
}

static lws_ss_state_return_t
bybit_state(void *userobj, void *h_src, lws_ss_constate_t state,
	      lws_ss_tx_ordinal_t ack)
{
	bybit_t *bin = (bybit_t *)userobj;

	lwsl_ss_info(bin->ss, "%s (%d), ord 0x%x",
		     lws_ss_state_name((int)state), state, (unsigned int)ack);

	switch (state) {

	case LWSSSCS_CONNECTED:
		lws_sul_schedule(lws_ss_get_context(bin->ss), 0, &bin->sul_hz,
				 sul_hz_cb, LWS_US_PER_SEC);
		range_reset(&bin->e_lat_range);
		range_reset(&bin->price_range);

		return LWSSSSRET_OK;

	case LWSSSCS_DISCONNECTED:
		lws_sul_cancel(&bin->sul_hz);
		break;

	default:
		break;
	}

	return LWSSSSRET_OK;
}

LWS_SS_INFO("bybit", bybit_t)
	.rx           = bybit_receive_callback,
	.tx           = bybit_transfer_callback,
	.state        = bybit_state,
};
