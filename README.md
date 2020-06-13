# TranslationPipe
Translation pipe is a small local tool to add standardized word of translation next to the matched key word. Suggestion and issue-report are welcome! :)

## Features
#### - It accept request links (uri) in an excel file(xlsx), download and standardize the links listed.
#### - If the links downloaded, it wouldn't download again, either the standardized links.
#### - It output results to the request links excel file.



## Sample Steps
### 1. Put links of original article to the requirement[XXX].xlsx file to <project root>/data/requirement/ folder. Sample file: https://github.com/HuangKaibo2017/TranslationPipe/blob/master/data/requirement/requirement20170830.xlsx.
### 2. On the command windows, run the script by:
```
python main.py -c
```
The results should appear in <project root>/data/standardized. 
  
Enjoy! 

## Tested Platforms
1. Python 3.6 with Windows 10 x64.

## Known Issues
1. Can't touch websites banned by the-great-wall;
2. Can't download contents loaded dynamically (i.e. loaded by js code) -- yes, i will deal with it later;

## TODOs
0. Change the file format of terminology from 机器之心;
1. No.2 of the Known Issues;
2. Work as a small SAAS;
3. Support word, pdf;
4. Support OCR of images.
5. download article translated by 机器之心、大数据文摘、数据派 as the training materials.

## Supports needed
1. sugguestion and issure report;
2. standard word contribution;
3. donation.

## Reference
1. 机器之心（Artificial-Intelligence-Terminology）：https://github.com/jiqizhixin/Artificial-Intelligence-Terminology#artificial-intelligence-terminology
2. 机器之心（Github 词汇集项目）：https://github.com/jiqizhixin/AI-Terminology-page#github-%E8%AF%8D%E6%B1%87%E9%9B%86%E9%A1%B9%E7%9B%AE
