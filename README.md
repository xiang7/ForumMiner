ForumMiner
==========

Some results:
Parallelize WLZW:

tested on 11M or 102400 lines of tweets
1 process 9.63s
2 process 6.35s

tested on 107M or 1024000 lines of tweets
1 process 106.63s
2 process 67.19s

Can test on a larger machine (ocean or mc18 with more processes)

Current task:
WLZW compression algorithm - read the source file, understand it and modify it into word level LZW
