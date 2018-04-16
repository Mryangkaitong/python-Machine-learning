SMS Spam Corpus v.0.1
---------------------

1. DESCRIPTION
--------------

The SMS Spam Corpus v.0.1 (hereafter the corpus) is a set of SMS tagged messages that have been collected for SMS Spam research. It contains two collections of SMS messages in English of 1084 and 1319 messages, tagged acording being legitimate (ham) or spam. 

1.1. Compilation
----------------

This corpus has been collected from free or free for research sources at the Web:

- A list of 202 legitimate messages, probably collected by Jon Stevenson, according to the HTML code of the Webpage. Only the text of the messages is available. We will call this corpus the Jon Stevenson Corpus (JSC). It is available at: http://www.demo.inty.net/Units/SMS/corpus.htm
- A subset of the NUS SMS Corpus (NSC), which is a corpus of about 10,000 legitimate messages collected for research at the Department of Computer Science at the National University of Singapore. The messages largely originate from Singaporeans and mostly from students attending the University. These messages were collected from volunteers who were made aware that their contributions were going to be made publicly available. The NUS SMS Corpus is avalaible at: http://www.comp.nus.edu.sg/~rpnlpir/downloads/corpora/smsCorpus/
- A collection of between 82 and 322 SMS spam messages extracted manually from the Grumbletext Web site. This is a UK forum in which cell phone users make public claims about SMS spam messages, most of them without reporting the very spam message received. The identification of the text of spam messages in the claims is a very hard and time-consuming task, and it involved carefully scanning hundreds of web pages. The Grumbletext Web site is: http://www.grumbletext.co.uk/

1.2. Statistics
---------------

There are two collections:

- The SMS Spam Corpus v.0.1 Small (file: english.txt) contains a total of 1002 legitimate messages and a total of 82 spam messages.
- The SMS Spam Corpus v.0.1 Big (file: english_big.txt) contains a total of 1002 legitimate messages and a total of 322 spam messages.

As reported at [3] in the about section, the big corpus average number of words per message is 15.72, and the average length of a word is 4.44 characters long.

1.3. Format
-----------

The files contain one message per line in raw text. Each line is finished with a coma-separated tag, which can be "ham" or "spam". Here are some examples:

Urgent! call 09061749602 from Landline. Your complimentary 4* Tenerife Holiday or £10,000 cash await collection SAE T&Cs BOX 528 HP20 1YF 150ppm 18+,spam
Ok then i come n pick u at engin?,ham
Anything lor... U decide...,ham

Messages are not chronologically sorted.

2. USAGE
--------

This corpus has been used in the following research.

The SMS Spam Corpus v.0.1 Small:

[1] Gómez Hidalgo, J.M., Cajigas Bringas, G., Puertas Sanz, E., Carrero García, F. Content Based SMS Spam Filtering. Dick Bulterman, David F. Brailsford (Eds.), Proceedings of the 2006 ACM Symposium on Document Engineering, Amsterdam, The Netherlands, ACM Press. Ámsterdam, The Netherlands, October 10-13, 2006. Preprint available at: http://www.esp.uem.es/jmgomez/papers/doceng06.pdf

[2] Cormack, G. V., Gómez Hidalgo, J. M., and Puertas Sánz, E. 2007. Feature engineering for mobile (SMS) spam filtering. In Proceedings of the 30th Annual international ACM SIGIR Conference on Research and Development in information Retrieval (Amsterdam, The Netherlands, July 23 - 27, 2007). SIGIR '07. ACM, New York, NY, 871-872. DOI= http://doi.acm.org/10.1145/1277741.1277951. Preprint available at: http://www.esp.uem.es/jmgomez/papers/sigir07.pdf

The SMS Spam Corpus v.0.1 Big:

[3] Cormack, G. V., Gómez Hidalgo, J. M., and  Puertas Sánz, E. 2007. Spam filtering for short messages. In Proceedings of the Sixteenth ACM Conference on Conference on information and Knowledge Management (Lisbon, Portugal, November 06 - 10, 2007). CIKM '07. ACM, New York, NY, 313-320. DOI= http://doi.acm.org/10.1145/1321440.1321486. Preprint available at: http://www.esp.uem.es/jmgomez/papers/cikm07.pdf

The NUS SMS Corpus has been used in the following research:

Yijue How and Min-Yen Kan (2005). Optimizing predictive text entry for short message service on mobile phones. In M. J. Smith & G. Salvendy (Eds.) Proc. of Human Computer Interfaces International (HCII 05). Lawrence Erlbaum Associates. Las Vegas, July 2005. ISBN 0805858075.

Yijue How (2004). Analysis of SMS Efficiency. Undergraduate Thesis. National University of Singapore.

Ming Fung Lee (2005). SMS Short Form Identification and Codec. Undergraduate Thesis. National University of Singapore. 

3. ABOUT
--------

The corpus has been collected by José María Gómez Hidalgo (http://www.esp.uem.es/jmgomez), and Enrique Puertas Sánz.

We would like to thank:
- Dr. Min-Yen Kan (http://www.comp.nus.edu.sg/~kanmy/) and his team for making the NUS SMS Corpus available. See: http://www.comp.nus.edu.sg/~rpnlpir/downloads/corpora/smsCorpus/
- Jon Stevenson for making his corpus available. See: http://www.demo.inty.net/Units/SMS/corpus.htm
- Vodafone Research Spain for supporting part of this research. See: http://www.vodafone.es
- Gordon V. Cormack for leading the experiments reported at [2] and [3]. See: http://plg.uwaterloo.ca/~gvcormac/

Dr. Min-Yen Kan is currently collecting a bigger SMS corpus at: http://wing.comp.nus.edu.sg:8080/SMSCorpus/

Other collections mentioned in the previous papers are:

- An Spanish SMS Spam Corpus, built by us under a strict Non-Disclosure Agreement with Vodafone. We can not publish this corpus.
- The Blog Comment Spam corpus collected by Mishne and Carmel and made available at: http://ilps.science.uva.nl/resources/commentspam
- The Email Spam Corpus provided for the TREC 2005 Spam Filtering Track, available at: http://plg.uwaterloo.ca/~gvcormac/spam/

4. LICENSE/DISCLAIMER
---------------------

We would appreciate if:

- In case you find this corpus useful, you make reference to the previous papers and the web page: http://www.esp.uem.es/jmgomez/smsspamcorpus in your papers, research, etc.
- You send us a message to jmgomezh@yahoo.es in case you make use of the corpus.

The SMS Spam Corpus v.0.1 is provided for free and with no limitations excepting:

1. José María Gómez Hidalgo, and Enrique Puertas Sanz, hold the copyrigth (c) for the SMS Spam Corpus v.0.1.

2. No Warranty/Use At Your Risk. THE CORPUS IS MADE AT NO CHARGE. ACCORDINGLY, THE CORPUS IS PROVIDED `AS IS,' WITHOUT WARRANTY OF ANY KIND, INCLUDING WITHOUT LIMITATION THE WARRANTIES THAT THEY ARE MERCHANTABLE, FIT FOR A PARTICULAR PURPOSE OR NON-INFRINGING. YOU ARE SOLELY RESPONSIBLE FOR YOUR USE, DISTRIBUTION, MODIFICATION, REPRODUCTION AND PUBLICATION OF THE CORPUS AND ANY DERIVATIVE WORKS THEREOF BY YOU AND ANY OF YOUR SUBLICENSEES (COLLECTIVELY, `YOUR CORPUS USE'). THE ENTIRE RISK AS TO YOUR CORPUS USE IS BORNE BY YOU. YOU AGREE TO INDEMNIFY AND HOLD THE COPYRIGHT HOLDERS, AND THEIR AFFILIATES HARMLESS FROM ANY CLAIMS ARISING FROM OR RELATING TO YOUR CORPUS USE.

3. Limitation of Liability. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR THEIR AFFILIATES, OR THE CORPUS CONTRIBUTING EDITORS, BE LIABLE FOR ANY INDIRECT, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES, INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS OF GOODWILL OR ANY AND ALL OTHER COMMERCIAL DAMAGES OR LOSSES, EVEN IF ADVISED OF THE POSSIBILITY THEREOF, AND REGARDLESS OF WHETHER ANY CLAIM IS BASED UPON ANY CONTRACT, TORT OR OTHER LEGAL OR EQUITABLE THEORY, RELATING OR ARISING FROM THE CORPUS, YOUR CORPUS USE OR THIS LICENSE AGREEMENT.