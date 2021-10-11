/*
 * lws-minimal-secure-streams-binance
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

#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

extern int test_result;
extern char fifo[64];
int fifo_descriptor = -1;

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
} binance_t;


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
	binance_t *bin = lws_container_of(sul, binance_t, sul_hz);

	/*
	 * We are called once a second to dump statistics on the connection
	 */

	lws_sul_schedule(lws_ss_get_context(bin->ss), 0, &bin->sul_hz,
			 sul_hz_cb, LWS_US_PER_SEC);

	test_result = 0;
}


static lws_ss_state_return_t
binance_rx(void *userobj, const uint8_t *in, size_t len, int flags)
{
	binance_t *bin = (binance_t *)userobj;
	uint64_t latency_us, now_us;
	char numbuf[16];
	uint64_t price;
	const char *p;
	size_t alen;

	if (fifo_descriptor >= 0) // the fifo is valid
	{
		write(fifo_descriptor, in, strlen(in));
		write(fifo_descriptor, "\n", 1);
	}

	return LWSSSSRET_OK;
}

static lws_ss_state_return_t
binance_state(void *userobj, void *h_src, lws_ss_constate_t state,
	      lws_ss_tx_ordinal_t ack)
{
	binance_t *bin = (binance_t *)userobj;

	lwsl_ss_info(bin->ss, "%s (%d), ord 0x%x",
		     lws_ss_state_name((int)state), state, (unsigned int)ack);

	switch (state) {

	case LWSSSCS_CONNECTED:
		lws_sul_schedule(lws_ss_get_context(bin->ss), 0, &bin->sul_hz,
				 sul_hz_cb, LWS_US_PER_SEC);

		mkfifo(fifo, 0666);
		fifo_descriptor = open(fifo, O_WRONLY);
		if (fifo_descriptor >= 0) // the fifo is valid
		{
			lwsl_user("Pipe %s created",fifo);
		}

		return LWSSSSRET_OK;

	case LWSSSCS_DISCONNECTED:
		if (fifo_descriptor >= 0) // the fifo is valid
		{
			close(fifo_descriptor);
			fifo_descriptor = -1;
			lwsl_user("Pipe %s closed",fifo);
		}

		lws_sul_cancel(&bin->sul_hz);
		break;

	default:
		break;
	}

	return LWSSSSRET_OK;
}

LWS_SS_INFO("binance", binance_t)
	.rx	      = binance_rx,
	.state    = binance_state,
};
