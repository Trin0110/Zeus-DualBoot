# Chinese and community research

Actual access results are preserved in `evidence/research/search-access.json`.
Searches included `骁龙8 Gen1 XNU`, `SM8450 iOS 移植`, `小米12 Pro 移植iOS`,
and Chinese Android/iOS port queries through GitHub repository search.

| Destination | Observed result |
| --- | --- |
| search.gitee.com | Proxy CONNECT 403 |
| gitcode.com | Proxy CONNECT 403 |
| search.bilibili.com | Proxy CONNECT 403 |
| www.coolapk.com | Proxy CONNECT 403 |
| xdaforums.com | Proxy CONNECT 403 |
| unixnu.com/devices/ | Proxy CONNECT 403 |
| github.com/search | HTTP 200; result metadata saved |

These are access restrictions, not evidence that ports do not exist. No claims
from blocked pages have been invented. The discovered `obaosp/UniXNU-sm8450-common`,
`obaosp/UniXNU-cupid` and `v1-727/UniXNU-sm8450-common` are additional UNVERIFIED
candidates initially found from search metadata. A subsequent source audit of all
three is recorded in `upstream-audit.md`; none has been hardware-verified here.
Search hits with marketing version claims are not hardware evidence. Chinese README files in accessible
UniXNU and HakiOS repositories provide additional leads, not independent proof.

Required custom domain additions for another search pass are exactly the six
blocked hostnames above. Redirects may require further observed host additions.
GitHub code research and local development can continue without those domains.
