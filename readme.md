# 问卷星后处理工具 v2.0


## 目的

在给学生布置作业的时候，问卷星是非常好用的一个工具。但是在批改作业的时候，问卷星是非常让人头疼的东西。毕竟没有人愿意对着excel那一堆文字去看。虽然问卷星自带了生成报告的功能，但是这功能需要付费。可既然我能下载（1）答卷数据，（2）问卷题目模板，以及（3）附件，况且附件保存年限非常短，肯定也要本地保存。那为什么不干脆用python做一个工具把这些数据生成本地能看的pdf呢？

### 这一版和v1的区别

[第一版](https://github.com/beneon/wjxConv)当时主要想解决的问题就是在excel里做一个指向问卷附件的文件链接。当时最早尝试使用python的urllib解析答卷数据中的链接文件，用这个链接文件匹配解压以后的附件。但是随着问卷星的进化，这一招不好用了。现在问卷星使用一套自己的命名方式，附件的文件名一般由答案序号、答案标示（一般默认使用姓名）、问题的前15个字符以及上传文件的文件名组成。之前的版本虽然也根据新的命名方式尝试做过更新，但是当时的屎山代码我已经无力维护。所以另起炉灶会更好一点。

## 组成

代码由wjx_model，wjx_view,以及充当template角色的reportlab_port三个大块组成。

### wjx_model

负责读取答题数据、学生信息文件和解析附件文件。

包含：

1. Curriculum类：读取解析整个课程的yaml config文件，按照课程内容生成对应的session类
2. Session类：一次实验或者一次作业作为一个session，负责读取答卷信息和解析附件，并且在两者之间交叉比对，更新answer entry中对应文件上传题的内容
3. SessionData类：由session生成的数据类，负责读取学生信息，和答卷信息中学生信息交叉比对，更新answer entry身份信息。实现了len和getitem方法，返回更新好的answer entry
4. AnswerEntry类：代表一个答卷数据，也实现了len和getitem方法，getitem返回其中答卷中的一列，以AnswerField表示
5. AnswerField类：AnswerEntry的下一级，具体表示一列数据
6. AttachmentParser类：表示当前session下的所有附件
7. AttachmentFileEntry类：表示一个附件文件

这一块代码基本上由3个层级组成，最顶层的是__init__下面的Curriculum和Session，Session下辖的AnswerEntry和AttachmentParser位于iters，而最下级则位于elems代码中


## 2024-07-08 学习记录2

现在可以：
1. 指定页眉页脚的内容了，数据从report_data里面读取
2. 初步尝试了根据report_lab['report_content']的内容更新story
3. 还给content部分加了外框
4. 此外调整了header和footer的位置

## 2024-07-08 reportlab学习记录

simple doc template中，onFirstPage和onLaterPages都需要提供一个处理函数，这个函数接受canvas以及doc两个参数，职责与pagetemplate类似

这个函数里面一般性的结构是：

```python
canvas.saveState()
...
canvas.restoreState()
```

对于canvas的各种操作都在saveState与restoreState之间进行。doc参数可以提供关于文档的各种信息。比如这个[gist里面](https://gist.github.com/nenodias/8c54500eb27884935d05b3ed3b0dd793)

```python
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
 
        # Header
        header = Paragraph('This is a multi-line header.  It goes on every page.   ' * 5, styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
 
        # Footer
        footer = Paragraph('This is a multi-line footer.  It goes on every page.   ' * 5, styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()
```

## 2024-07-05 记录

问卷星部分完成了以下功能：
1. 给问卷设计模板每一个问题前面手动加上一个`>`的话，这个程序可以识别所有问题（包括段落说明），然后将之与问卷数据相匹配
2. 读取问卷数据，以AnswerField代表每一个答案中的各个问题
3. 将附件与AnswerField相匹配，一个问卷支持多个文件上传field

问卷信息处理好以后最后是要输出的。之前我使用python下的docx库，这个玩意问题一点也不必reportlab少，文档和使用的人还更少。所以还不如直接转到reportlab。

关于reportlab：现在可以比较粗略的输出一个文档，但是还没有到可以实用化的地步。接下来需要按照platypus的流程构建文档的输出模型

实现思路：

1. 沿用SimpleDocTemplate, 手动设置myFirstPage()和myLaterPages()两个函数（两个函数在ExpReport类里面实现(实验一下这样能不能保证数据传入)
2. 在ExpReport中主要负责组织传入数据，构建story

猜测：Frame应该是用在pagetemplate一类的地方

## init
之前的版本最大的问题是没有把问卷模板和问卷数据联动。这一版想办法解决这个问题。

目前包括student manager，data file parser以及question template parser三块，最后输出包括答题数据的json文件与前端交互。至于之后是用word proc生成docx还是用vue3输出，这个再说。现在倾向于使用vue3输出比较好。

