# lws secure streams bybit

This is a Secure Streams version of bybit ws client.

"policy.json" contains all the information about endpoints, protocols and
connection validation, tagged by streamtype name.


The secure stream object represents a nailed-up connection that outlives any
single socket connection, and can manage reconnections / retries according to
the policy to keep the connection nailed up automatically.

Secure Streams provides the same simplified communication api without any
protocol dependencies.

## build

Lws must have been built with `LWS_ROLE_WS=1`, `LWS_WITH_SECURE_STREAMS=1`, and
`LWS_WITHOUT_EXTENSIONS=0`

```
 $ cmake . && make
```

## Commandline Options

Option|Meaning
---|---
-d|Set logging verbosity

## usage

```
$ ./lws-bybit 
[2021/09/30 19:35:17:2236] U: LWS minimal Secure Streams binance client
[2021/09/30 19:35:17:2238] N: LWS: 4.2.99-v4.2.0-207-g9975de34, NET CLI SRV H1 H2 WS SS-JSON-POL ConMon IPv6-absent
[2021/09/30 19:35:17:2239] N:  ++ [wsi|0|pipe] (1)
[2021/09/30 19:35:17:2239] N:  ++ [vh|0|netlink] (1)
[2021/09/30 19:35:17:2312] N:  ++ [vh|1|starfield||-1] (2)
[2021/09/30 19:35:17:2336] N:  ++ [wsiSScli|0|binance] (1)
[2021/09/30 19:35:17:2353] N: [wsiSScli|0|binance]: lws_ss_check_next_state_ss: (unset) -> LWSSSCS_CREATING
[2021/09/30 19:35:17:2359] N: [wsiSScli|0|binance]: lws_ss_check_next_state_ss: LWSSSCS_CREATING -> LWSSSCS_CONNECTING
[2021/09/30 19:35:17:2367] N:  ++ [wsicli|0|WS/h1/stream.bybit.com/([wsiSScli|0|binance])] (1)
[2021/09/30 19:35:17:3130] N: lws_gate_accepts: on = 0
[2021/09/30 19:35:17:3508] N: lws_gate_accepts: on = 0
[2021/09/30 19:35:18:2140] N: lws_client_reset: REDIRECT stream.bybit.com:443, path='realtime', ssl = 1, alpn='http/1.1'
[2021/09/30 19:35:18:2144] N: lws_gate_accepts: on = 0
[2021/09/30 19:35:18:2519] N: lws_gate_accepts: on = 0
[2021/09/30 19:35:18:2901] N: lws_gate_accepts: on = 0
[2021/09/30 19:35:19:1553] N: [wsiSScli|0|binance]: lws_ss_check_next_state_ss: LWSSSCS_CONNECTING -> LWSSSCS_CONNECTED
^C[2021/09/30 19:36:08:0273] N:  -- [wsi|0|pipe] (0) 50.803s
[2021/09/30 19:36:08:0273] N: [wsiSScli|0|binance]: lws_ss_check_next_state_ss: LWSSSCS_CONNECTED -> LWSSSCS_DISCONNECTED
[2021/09/30 19:36:08:0280] N: lws_gate_accepts: on = 0
[2021/09/30 19:36:08:0281] N:  -- [vh|1|starfield||-1] (1) 50.796s
[2021/09/30 19:36:08:0281] N:  -- [wsicli|0|WS/h1/stream.bybit.com/([wsiSScli|0|binance])] (0) 50.791s
[2021/09/30 19:36:08:0282] N:  -- [vh|0|netlink] (0) 50.804s
[2021/09/30 19:36:08:0282] N: [wsiSScli|0|binance]: lws_ss_check_next_state_ss: LWSSSCS_DISCONNECTED -> LWSSSCS_DESTROYING
[2021/09/30 19:36:08:0282] N:  -- [wsiSScli|0|binance] (0) 50.794s
[2021/09/30 19:36:08:0283] U: Completed: OK (seen expected 0)
...
```
