---
publishDate: 2024-09-05T00:00:00Z
title: '单元测试原则、实践与模式（一）'
excerpt: '本章内容涵盖单元测试的现状、目标，以及使用覆盖指标来衡量测试套件的质量。'
category: '测试'
tags:
  - 单元测试
metadata:
  canonical: https://nobug.world/blogs/8383/
---

> 译者声明：本译文仅作为学习的记录，不作为任务商业用途，如有侵权请告知我删除。  
> **本文禁止转载！**  
> 请支持原书正版：[https://www.manning.com/books/unit-testing](https://www.manning.com/books/unit-testing)


# [](#第一章：单元测试的目标 "第一章：单元测试的目标")第一章：单元测试的目标

**Chapter1 The goal of unit testing**

This chapter covers 本章内容涵盖

*   The state of unit testing 单元测试的现状
*   The goal of unit testing 单元测试的目标
*   Consequences of having a bad test suite 拥有一个糟糕的测试套件的后果
*   Using coverage metrics to measure test suite quality 使用覆盖率指标来衡量测试套件的质量
*   Attributes of a successful test suite 一个成功的测试套件的属性

> 译者注：
> 
> “test suite” 通常被翻译为“测试套件”或“测试集”。这两个术语都指的是一系列自动化测试的集合，这些测试通常被组织在一起执行，以便验证软件的不同部分是否按预期工作。

Learning unit testing doesn’t stop at mastering the technical bits of it, such as your favorite test framework, mocking library, and so on. There’s much more to unit testing than the act of writing tests. You always have to strive to achieve the best return on the time you invest in unit testing, minimizing the effort you put into tests and maximizing the benefits they provide. Achieving both things isn’t an easy task.

学习单元测试并不仅仅是掌握它的技术部分，比如你最喜欢的测试框架、mocking 库等等。单元测试的内容远远多于编写测试的行为。你总是要努力使你在单元测试中投入的时间得到最好的回报，使你在测试中投入的精力最小化，使它们提供的好处最大化。实现这两点并不是一件容易的事。

It’s fascinating to watch projects that have achieved this balance: they grow effortlessly, don’t require much maintenance, and can quickly adapt to their cusomers’ ever-changing needs. It’s equally frustrating to see projects that failed to do so. Despite all the effort and an impressive number of unit tests, such projects drag on slowly, with lots of bugs and upkeep costs.

看到那些实现了这种平衡的项目是令人着迷的：它们毫不费力地增长，不需要太多的维护，并能迅速适应客户不断变化的需求。同样令人沮丧的是，看到那些未能做到的项目。尽管付出了所有的努力和数量惊人的单元测试，这样的项目还是拖得很慢，有很多的错误和维护费用。

That’s the difference between various unit testing techniques. Some yield great outcomes and help maintain software quality. Others don’t: they result in tests that don’t contribute much, break often, and require a lot of maintenance in general. What you learn in this book will help you differentiate between good and bad unit testing techniques. You’ll learn how to do a cost-benefit analysis of your tests and apply proper testing techniques in your particular situation. You’ll also learn how to avoid common anti-patterns—patterns that may make sense at first but lead to trouble down the road.

这就是各种单元测试技术之间的区别。有些产生了很好的结果，有助于保持软件质量。另一些则不然：它们的测试没有什么贡献，经常出错，而且一般需要大量的维护。你在本书中学到的东西将帮助你区分好的和坏的单元测试技术。你将学会如何对你的测试进行成本效益分析，并在你的特定情况下应用适当的测试技术。你还将学习如何避免常见的反模式–这些模式一开始可能有意义，但会导致日后的麻烦。

But let’s start with the basics. This chapter gives a quick overview of the state of unit testing in the software industry, describes the goal behind writing and maintaining tests, and provides you with the idea of what makes a test suite successful.

但让我们从基础知识开始。本章对软件行业中的单元测试的状况做了一个快速的概述，描述了编写和维护测试背后的目标，并为你提供了什么使测试套件成功的概念。

## [](#1-1-单元测试的现状 "1.1 单元测试的现状")1.1 单元测试的现状

**The current state of unit testing**

For the past two decades, there’s been a push toward adopting unit testing. The push has been so successful that unit testing is now considered mandatory in most companies. Most programmers practice unit testing and understand its importance. There’s no longer any dispute as to whether you should do it. Unless you’re working on a throwaway project, the answer is, yes, you do.

在过去的二十年里，人们一直在推动采用单元测试。这种推动是如此成功，以至于单元测试现在被认为是大多数公司的必修课。大多数程序员都在实践单元测试，并理解其重要性。对于是否应该做单元测试，已经没有任何争议了。除非你正在做一个废弃的项目，否则答案是，是的，你要做。

When it comes to enterprise application development, almost every project includes at least some unit tests. A significant percentage of such projects go far beyond that: they achieve good code coverage with lots and lots of unit and integration tests. The ratio between the production code and the test code could be anywhere between 1:1 and 1:3 (for each line of production code, there are one to three lines of test code). Sometimes, this ratio goes much higher than that, to a whopping 1:10.

当涉及到企业应用开发时，几乎每个项目都至少包括一些单元测试。其中相当大比例的项目远不止于此：他们通过大量的单元和集成测试来实现良好的代码覆盖。生产代码和测试代码之间的比例可能在 1:1 和 1:3 之间（每行生产代码，有 1 到 3 行测试代码）。有时，这个比例会比这高得多，达到惊人的 1:10。

But as with all new technologies, unit testing continues to evolve. The discussion has shifted from “Should we write unit tests?” to “What does it mean to write good unit tests?” This is where the main confusion still lies.

但是就像所有的新技术一样，单元测试也在不断发展。讨论已经从 “我们应该写单元测试吗？”转向 “写好单元测试意味着什么？” 这就是主要的困惑所在。

You can see the results of this confusion in software projects. Many projects have automated tests; they may even have a lot of them. But the existence of those tests often doesn’t provide the results the developers hope for. It can still take programmers a lot of effort to make progress in such projects. New features take forever to implement, new bugs constantly appear in the already implemented and accepted functionality, and the unit tests that are supposed to help don’t seem to mitigate this situation at all. They can even make it worse.

你可以在软件项目中看到这种困惑的结果。许多项目都有自动化测试；他们甚至可能有很多的自动化测试。但这些测试的存在往往不能提供开发人员希望的结果。在这样的项目中，程序员仍然可能需要花费大量的精力来推进。新功能的实现需要很长时间，在已经实现和接受的功能中不断出现新的bug，而本应提供帮助的单元测试似乎根本没有缓解这种情况。它们甚至会使情况变得更糟。

It’s a horrible situation for anyone to be in—and it’s the result of having unit tests that don’t do their job properly. The difference between good and bad tests is not merely a matter of taste or personal preference, it’s a matter of succeeding or failing at this critical project you’re working on.

这对任何人来说都是一种可怕的情况–这是由单元测试没有正确完成其工作所造成的。好的和坏的测试之间的区别不仅仅是一个品味或个人偏好的问题，它关系到你正在进行的这个关键项目的成功或失败。

It’s hard to overestimate the importance of the discussion of what makes a good unit test. Still, this discussion isn’t occurring much in the software development industry today. You’ll find a few articles and conference talks online, but I’ve yet to see any comprehensive material on this topic.

关于什么是好的单元测试的讨论，其重要性怎么估计都不为过。尽管如此，这种讨论在今天的软件开发行业中并没有发生多少。你可以在网上找到一些文章和会议演讲，但我还没有看到关于这个话题的全面的材料。

The situation in books isn’t any better; most of them focus on the basics of unit testing but don’t go much beyond that. Don’t get me wrong. There’s a lot of value in such books, especially when you are just starting out with unit testing. However, the learning doesn’t end with the basics. There’s a next level: not just writing tests, but doing unit testing in a way that provides you with the best return on your efforts. When you reach this point, most books pretty much leave you to your own devices to figure out how to get to that next level.

书籍中的情况也没有好到哪里去；大多数书都集中在单元测试的基础知识上，但并没有超出这个范围。不要误会我的意思。这类书有很多价值，特别是当你刚开始做单元测试时。然而，学习并不以基础知识为终点。下一个层次：不仅仅是写测试，而是以一种能够为你的努力提供最佳回报的方式进行单元测试。当你达到这一点时，大多数书都让你自己去想如何达到下一个层次。

This book takes you there. It teaches a precise, scientific definition of the ideal unit test. You’ll see how this definition can be applied to practical, real-world examples. My hope is that this book will help you understand why your particular project may have gone sideways despite having a good number of tests, and how to correct its course for the better.

这本书把你带到那里。它教给你一个关于理想单元测试的精确、科学的定义。你会看到这个定义如何应用于实际的、真实世界的例子。我希望这本书能帮助你理解为什么你的特定项目尽管有大量的测试，但还是走偏了，以及如何纠正它的方向，使之变得更好。

You’ll get the most value out of this book if you work in enterprise application development, but the core ideas are applicable to any software project.

如果你从事企业应用开发工作，你将从本书中获得最大的价值，但其核心思想适用于任何软件项目。

> What is an enterprise application?
> 
> 什么是企业应用程序？
> 
> An enterprise application is an application that aims at automating or assisting an organization’s inner processes. It can take many forms, but usually the characteristics of an enterprise software are
> 
> 企业应用软件是一种旨在实现组织内部流程自动化或协助组织的应用软件。它可以有多种形式，但通常企业软件的特点是
> 
> *   High business logic complexity 业务逻辑高度复杂
> *   Long project lifespan 项目周期长
> *   Moderate amounts of data 适度的数据量
> *   Low or moderate performance requirements 低度或中度的性能要求

## [](#1-2-单元测试的目标 "1.2 单元测试的目标")1.2 单元测试的目标

\*\*The goal of unit testing \*\*

Before taking a deep dive into the topic of unit testing, let’s step back and consider the goal that unit testing helps you to achieve. It’s often said that unit testing practices lead to a better design. And it’s true: the necessity to write unit tests for a code base normally leads to a better design. But that’s not the main goal of unit testing; it’s merely a pleasant side effect.

在深入探讨单元测试的话题之前，让我们退一步考虑单元测试帮助你实现的目标。人们常说，单元测试的实践会带来更好的设计。这是真的：为代码库编写单元测试的必要性通常会导致更好的设计。但这并不是单元测试的主要目标；它只是一个令人愉快的副作用。

> The relationship between unit testing and code design
> 
> 单元测试和代码设计之间的关系
> 
> The ability to unit test a piece of code is a nice litmus test, but it only works in one direction. It’s a good negative indicator—it points out poor-quality code with relatively high accuracy. If you find that code is hard to unit test, it’s a strong sign that the code needs improvement. The poor quality usually manifests itself in tight coupling, which means different pieces of production code are not decoupled from each other enough, and it’s hard to test them separately.
> 
> 代码单元测试的能力是一个很好的检验标准，但它只适用于一种情况。它是一个很好的负面指标——它能够相对高精确度地指出质量较差的代码。如果你发现代码很难进行单元测试，那么这往往是代码需要改进的一个强烈信号。质量差通常表现为紧密耦合，这意味着不同部分的生产代码之间缺乏足够解耦，难以单独测试它们。
> 
> Unfortunately, the ability to unit test a piece of code is a bad positive indicator. The fact that you can easily unit test your code base doesn’t necessarily mean it’s of good quality. The project can be a disaster even when it exhibits a high degree of decoupling.
> 
> 不幸的是，对一段代码进行单元测试的能力不是一个好的正面指标。你可以很容易地对你的代码库进行单元测试的事实并不一定意味着它的质量很好。即使项目表现出高度的解耦性，它也可能是一场灾难。

What is the goal of unit testing, then? The goal is to enable sustainable growth of the software project. The term sustainable is key. It’s quite easy to grow a project, especially when you start from scratch. It’s much harder to sustain this growth over time.

那么，单元测试的目标是什么？目标是使软件项目的可持续发展。可持续这个词是关键。增长一个项目是很容易的，特别是当你从头开始的时候。但随着时间的推移，要维持这种增长就难得多了。

Figure 1.1 shows the growth dynamic of a typical project without tests. You start off quickly because there’s nothing dragging you down. No bad architectural decisions have been made yet, and there isn’t any existing code to worry about. As time goes by, however, you have to put in more and more hours to make the same amount of progress you showed at the beginning. Eventually, the development speed slows down significantly, sometimes even to the point where you can’t make any progress whatsoever.

图1.1显示了一个没有测试的典型项目的增长动态。你开始的时候很快，因为没有什么拖累你。还没有做出糟糕的架构决策，也没有任何现有的代码需要担心。然而，随着时间的推移，你必须投入越来越多的时间来取得与开始时相同的进展。最终，开发速度明显减慢，有时甚至到了你无法取得任何进展的地步。

![image-20230409175531352](~/assets/images/unit-testing-1/image-20230409175531352-1725371189717-1.png)

Figure 1.1 The difference in growth dynamics between projects with and without tests. A project without tests has a head start but quickly slows down to the point that it’s hard to make any progress.

图1.1 有测试和无测试的项目在增长动态的差异。一个没有测试的项目有一个领先的起点，但很快就会放慢速度，以至于很难取得任何进展。

This phenomenon of quickly decreasing development speed is also known as software entropy. Entropy (the amount of disorder in a system) is a mathematical and scientific concept that can also apply to software systems. (If you’re interested in the math and science of entropy, look up the second law of thermodynamics.)

这种开发速度迅速下降的现象也被称为软件熵。熵（一个系统中的无序程度）是一个数学和科学概念，也可以适用于软件系统。(如果你对熵的数学和科学感兴趣，可以查查热力学第二定律）。

In software, entropy manifests in the form of code that tends to deteriorate. Each time you change something in a code base, the amount of disorder in it, or entropy, increases. If left without proper care, such as constant cleaning and refactoring, the system becomes increasingly complex and disorganized. Fixing one bug introduces more bugs, and modifying one part of the software breaks several others—it’s like a domino effect. Eventually, the code base becomes unreliable. And worst of all, it’s hard to bring it back to stability.

在软件中，熵的表现形式是趋于恶化的代码。每当你改变代码库中的某些东西时，其中的无序量或熵就会增加。如果没有适当的照顾，如不断的清理和重构，系统会变得越来越复杂和无序。修复一个错误会带来更多的错误，修改软件的一个部分会破坏其他几个部分–这就像多米诺效应。最终，代码库变得不可靠。最糟糕的是，很难使它恢复稳定。

Tests help overturn this tendency. They act as a safety net—a tool that provides insurance against a vast majority of regressions. Tests help make sure the existing functionality works, even after you introduce new features or refactor the code to better fit new requirements.

测试有助于扭转这种趋势。他们充当了一个安全网–一个提供保险的工具，以防止绝大多数的回归。测试有助于确保现有的功能正常工作，即使在你引入新的功能或重构代码以更好地适应新的需求之后。

> DEFINITION
> 
> A regression is when a feature stops working as intended after a certain event (usually, a code modification). The terms regression and software bug are synonyms and can be used interchangeably.
> 
> 回归是指在某个事件（通常是代码修改）发生后，一个功能不再按预期工作。术语回归和软件错误是同义词，可以互换使用。

The downside here is that tests require initial—sometimes significant—effort. But they pay for themselves in the long run by helping the project to grow in the later stages. Software development without the help of tests that constantly verify the code base simply doesn’t scale.

这里的缺点是，测试需要在初始阶段投入大量精力。但从长远来看，它们有助于项目在后期发展，从而为自己带来回报。如果没有测试不断验证代码库，软件开发根本无法扩展。

Sustainability and scalability are the keys. They allow you to maintain development speed in the long run.

可持续性和可扩展性是关键。它们可以让你在长期内保持开发速度。

### [](#1-2-1-什么是好或坏的测试？ "1.2.1 什么是好或坏的测试？")1.2.1 什么是好或坏的测试？

**What makes a good or bad test?**

Although unit testing helps maintain project growth, it’s not enough to just write tests. Badly written tests still result in the same picture.

虽然单元测试有助于保持项目的增长，但仅仅写测试是不够的。写得不好的测试仍然会导致同样的情况。

As shown in figure 1.2, bad tests do help to slow down code deterioration at the beginning: the decline in development speed is less prominent compared to the situation with no tests at all. But nothing really changes in the grand scheme of things. It might take longer for such a project to enter the stagnation phase, but stagnation is still inevitable.

如图1.2所示，糟糕的测试在开始时确实有助于减缓代码的恶化：与完全没有测试的情况相比，开发速度的下降并不突出。但从总体上看，没有什么真正的变化。这样的项目可能需要更长的时间来进入停滞期，但停滞期仍然是不可避免的。

![image-20230409175736190](~/assets/images/unit-testing-1/image-20230409175736190-1725371776227-4.png)

Figure 1.2 The difference in growth dynamics between projects with good and bad tests. A project with badly written tests exhibits the properties of a project with good tests at the beginning, but it eventually falls into the stagnation phase.

图1.2 有好的测试和坏的测试的项目之间增长动态的差异。一个测试写得很差的项目在开始时表现出具有良好测试的项目的特性，但它最终会落入停滞阶段。

Remember, not all tests are created equal. Some of them are valuable and contribute a lot to overall software quality. Others don’t. They raise false alarms, don’t help you catch regression errors, and are slow and difficult to maintain. It’s easy to fall into the trap of writing unit tests for the sake of unit testing without a clear picture of whether it helps the project.

记住，不是所有的测试都是一样的。有些测试是有价值的，对整个软件质量有很大的贡献。其他的则不然。它们会引起错误的警报，不能帮助你捕获回归的错误，而且速度慢，难以维护。我们很容易落入为单元测试而写单元测试的陷阱，而不清楚它是否有助于项目的发展。

You can’t achieve the goal of unit testing by just throwing more tests at the project. You need to consider both the test’s value and its upkeep cost. The cost component is determined by the amount of time spent on various activities:

你不能仅仅通过在项目中抛出更多的测试来实现单元测试的目标。你需要同时考虑测试的价值和它的维护成本。成本部分是由花在各种活动上的时间决定的：

*   Refactoring the test when you refactor the underlying code 重构底层代码时重构测试
*   Running the test on each code change 在每次代码修改时运行测试
*   Dealing with false alarms raised by the test 处理由测试引起的错误警报
*   Spending time reading the test when you’re trying to understand how the underlying code behaves 当你试图了解底层代码的行为方式时，花时间阅读测试。

It’s easy to create tests whose net value is close to zero or even is negative due to high maintenance costs. To enable sustainable project growth, you have to exclusively focus on high-quality tests—those are the only type of tests that are worth keeping in the test suite.

由于维护成本高，很容易创建净值接近于零甚至是负值的测试。为了实现项目的可持续发展，你必须专门关注高质量的测试–这些是唯一值得保留在测试套件中的测试类型。

> Production code vs. test code 生产代码 vs. 测试代码
> 
> People often think production code and test code are different. Tests are assumed to be an addition to production code and have no cost of ownership. By extension, people often believe that the more tests, the better. This isn’t the case. Code is a liability, not an asset. The more code you introduce, the more you extend the surface area for potential bugs in your software, and the higher the project’s upkeep cost. It’s always better to solve problems with as little code as possible.
> 
> 人们经常认为生产代码和测试代码是不同的。测试被认为是对生产代码的补充，并且没有所有权成本。推而广之，人们常常认为测试越多越好。事实并非如此。代码是一种责任，而不是一种资产。你引入的代码越多，你就越能扩大软件中潜在错误的表面积，项目的维护成本也就越高。用尽可能少的代码来解决问题总是更好的。
> 
> Tests are code, too. You should view them as the part of your code base that aims at solving a particular problem: ensuring the application’s correctness. Unit tests, just like any other code, are also vulnerable to bugs and require maintenance.
> 
> 测试也是代码。你应该把它们看作是代码库的一部分，目的是解决一个特殊的问题：确保应用程序的正确性。单元测试，就像其他的代码一样，也容易出现错误，需要维护。

It’s crucial to learn how to differentiate between good and bad unit tests. I cover this topic in chapter 4.

学习如何区分好的和坏的单元测试是至关重要的。我在第四章介绍了这个话题。

## [](#1-3-使用覆盖指标来衡量测试套件的质量 "1.3 使用覆盖指标来衡量测试套件的质量")1.3 使用覆盖指标来衡量测试套件的质量

**Using coverage metrics to measure test suite quality**

In this section, I talk about the two most popular coverage metrics—code coverage and branch coverage—how to calculate them, how they’re used, and problems with them. I’ll show why it’s detrimental for programmers to aim at a particular coverage number and why you can’t just rely on coverage metrics to determine the quality of your test suite.

在本节中，我将谈论两个最流行的覆盖率指标–代码覆盖率和分支覆盖率–如何计算它们，如何使用它们，以及它们的问题。我将说明为什么程序员以特定的覆盖率为目标是有害的，以及为什么你不能仅仅依靠覆盖率指标来确定你的测试套件的质量。

> DEFINITION
> 
> A coverage metric shows how much source code a test suite executes, from none to 100%.
> 
> 覆盖率指标显示了一个测试套件执行了多少源代码，从0 到 100%。

There are different types of coverage metrics, and they’re often used to assess the quality of a test suite. The common belief is that the higher the coverage number, the better.

有不同类型的覆盖率指标，它们经常被用来评估一个测试套件的质量。人们普遍认为，覆盖率数字越高越好。

Unfortunately, it’s not that simple, and coverage metrics, while providing valuable feedback, can’t be used to effectively measure the quality of a test suite. It’s the same situation as with the ability to unit test the code: coverage metrics are a good negative indicator but a bad positive one.

不幸的是，事实并非如此简单，覆盖率指标虽然提供了有价值的反馈，但不能用来有效地衡量测试套件的质量。这和单元测试代码的能力是一样的情况：覆盖率指标是一个好的负面指标，但却是一个坏的正面指标。

If a metric shows that there’s too little coverage in your code base—say, only 10%— that’s a good indication that you are not testing enough. But the reverse isn’t true: even 100% coverage isn’t a guarantee that you have a good-quality test suite. A test suite that provides high coverage can still be of poor quality.

如果一个指标显示你的代码库中的覆盖率太低–比如说，只有10%–这就很好地说明你的测试还不够。但反过来说也不对：即使是100%的覆盖率也不能保证你有一个高质量的测试套件。一个提供高覆盖率的测试套件仍然可以是低质量的。

I already touched on why this is so—you can’t just throw random tests at your project with the hope those tests will improve the situation. But let’s discuss this problem in detail with respect to the code coverage metric.

我已经谈到了为什么会这样–你不能只是在你的项目中随意地抛出测试，希望这些测试能改善情况。但是，让我们来详细讨论一下这个与代码覆盖率指标有关的问题。

### [](#1-3-1-理解代码覆盖率指标 "1.3.1 理解代码覆盖率指标")1.3.1 理解代码覆盖率指标

**Understanding the code coverage metric**

The first and most-used coverage metric is code coverage, also known as test coverage; see figure 1.3. This metric shows the ratio of the number of code lines executed by at least one test and the total number of lines in the production code base.

第一个也是最常用的覆盖率指标是代码覆盖率，也被称为测试覆盖率；见图1.3。这个指标显示了至少由一个测试执行的代码行数与生产代码库中的总行数的比率。

![image-20230409180044244](~/assets/images/unit-testing-1/image-20230409180044244.png)

Figure 1.3 The code coverage (test coverage) metric is calculated as the ratio between the number of code lines executed by the test suite and the total number of lines in the production code base.

图1.3 代码覆盖率（测试覆盖率）指标的计算方法是测试套件执行的代码行数与生产代码库中的总行数的比率。

Let’s see an example to better understand how this works. Listing 1.1 shows an IsStringLong method and a test that covers it. The method determines whether a string provided to it as an input parameter is long (here, the definition of long is any string with the length greater than five characters). The test exercises the method using “abc” and checks that this string is not considered long.

让我们看一个例子来更好地理解它的工作原理。清单1.1显示了一个 IsStringLong 方法和一个涵盖它的测试。该方法确定一个作为输入参数提供给它的字符串是否是长的（这里，长的定义是任何长度大于5个字符的字符串）。测试使用 “abc “ 来执行该方法，并检查这个字符串是否被认为是长字符串。

Listing 1.1 A sample method partially covered by a test 清单1.1 一个被测试部分覆盖的示例方法

![image-20230409180204570](~/assets/images/unit-testing-1/image-20230409180204570.png)

![image-20230409180216213](~/assets/images/unit-testing-1/image-20230409180216213.png)

It’s easy to calculate the code coverage here. The total number of lines in the method is five (curly braces count, too). The number of lines executed by the test is four—the test goes through all the code lines except for the return true; statement. This gives us 4/5 = 0.8 = 80% code coverage.

计算这里的代码覆盖率很容易。该方法的总行数是 5 行（大括号也算）。测试所执行的行数是 4 行–测试通过了所有的代码行，除了`return true;` 语句。这给了我们 4/5 = 0.8 = 80% 的代码覆盖率。

Now, what if I refactor the method and inline the unnecessary if statement, like this?

现在，如果我重构该方法并 inline 不必要的 if 语句，像这样，会怎么样？

![image-20230409180242284](~/assets/images/unit-testing-1/image-20230409180242284.png)

Does the code coverage number change? Yes, it does. Because the test now exercises all three lines of code (the return statement plus two curly braces), the code coverage increases to 100%.

编码范围的编号会改变吗？是的，会的。因为测试现在执行了所有三行代码（返回语句加上两个大括号），代码覆盖率增加到 100%。

But did I improve the test suite with this refactoring? Of course not. I just shuffled the code inside the method. The test still verifies the same number of possible outcomes.

但我是否通过这次重构改进了测试套件？当然没有。我只是把方法里面的代码整理了一下。测试仍然验证了相同数量的可能结果。

This simple example shows how easy it is to game the coverage numbers. The more compact your code is, the better the test coverage metric becomes, because it only accounts for the raw line numbers. At the same time, squashing more code into less space doesn’t (and shouldn’t) change the value of the test suite or the maintainability of the underlying code base.

这个简单的例子说明了在覆盖率上做文章是多么容易。你的代码越紧凑，测试覆盖率指标就越好，因为它只考虑了原始行数。同时，把更多的代码压缩到更小的空间里并不会（也不应该）改变测试套件的价值或基础代码库的可维护性。

### [](#1-3-2-理解分支覆盖率指标 "1.3.2 理解分支覆盖率指标")1.3.2 理解分支覆盖率指标

**Understanding the branch coverage metric**

Another coverage metric is called branch coverage. Branch coverage provides more precise results than code coverage because it helps cope with code coverage’s shortcomings. Instead of using the raw number of code lines, this metric focuses on control structures, such as if and switch statements. It shows how many of such control structures are traversed by at least one test in the suite, as shown in figure 1.4.

另一个覆盖率指标被称为分支覆盖率。分支覆盖率比代码覆盖率提供更精确的结果，因为它有助于应对代码覆盖率的缺陷。这个指标不是使用原始的代码行数，而是关注控制结构，例如 if 和 switch 语句。它显示了有多少这样的控制结构被套件中的至少一个测试所遍历，如图 1.4 所示。

![image-20230409181832412](~/assets/images/unit-testing-1/image-20230409181832412.png)

Figure 1.4 The branch metric is calculated as the ratio of the number of code branches exercised by the test suite and the total number of branches in the production code base.

图 1.4 分支指标的计算方法是测试套件执行的代码分支数量与生产代码库中的分支总数的比率。

To calculate the branch coverage metric, you need to sum up all possible branches in your code base and see how many of them are visited by tests. Let’s take our previous example again:

为了计算分支覆盖率指标，你需要将代码库中所有可能的分支加起来，看看有多少分支被测试所访问。让我们再来看看我们之前的例子：

![image-20230409181855248](~/assets/images/unit-testing-1/image-20230409181855248.png)

There are two branches in the IsStringLong method: one for the situation when the length of the string argument is greater than five characters, and the other one when it’s not. The test covers only one of these branches, so the branch coverage metric is 1/2 = 0.5 = 50%. And it doesn’t matter how we represent the code under test— whether we use an if statement as before or use the shorter notation. The branch coverage metric only accounts for the number of branches; it doesn’t take into consideration how many lines of code it took to implement those branches.

IsStringLong 方法中有两个分支：一个是字符串参数的长度大于 5 个字符时的情况，另一个是不大于 5 个字符时的情况。测试只覆盖了其中一个分支，所以分支覆盖率指标是 1/2 = 0.5 = 50%。我们如何表示测试中的代码并不重要–我们是像以前一样使用 if 语句还是使用更短的符号。分支覆盖率指标只考虑了分支的数量，并没有考虑到实现这些分支需要多少行代码。

Figure 1.5 shows a helpful way to visualize this metric. You can represent all possible paths the code under test can take as a graph and see how many of them have been traversed. IsStringLong has two such paths, and the test exercises only one of them.

图 1.5 展示了一种可视化这一指标的有用方法。你可以把被测试的代码可能采取的所有路径用图表示出来，看看其中有多少被穿越了。IsStringLong 有两条这样的路径，而测试只测试了其中一条。

![image-20230409181920767](~/assets/images/unit-testing-1/image-20230409181920767.png)

Figure 1.5 The method IsStringLong represented as a graph of possible code paths. Test covers only one of the two code paths, thus providing 50% branch coverage.

图1.5 IsStringLong 方法表示为可能的代码路径图。测试只覆盖了两条代码路径中的一条，因此提供了 50% 的分支覆盖。

### [](#1-3-3-覆盖率指标的问题 "1.3.3 覆盖率指标的问题")1.3.3 覆盖率指标的问题

**Problems with coverage metrics**

Although the branch coverage metric yields better results than code coverage, you still can’t rely on either of them to determine the quality of your test suite, for two reasons:

尽管分支覆盖率指标比代码覆盖率产生更好的结果，但你仍然不能依靠它们中的任何一个来确定你的测试套件的质量，原因有二：

*   You can’t guarantee that the test verifies all the possible outcomes of the system under test. 你无法保证测试验证了被测系统的所有可能结果。
*   No coverage metric can take into account code paths in external libraries. 没有一个覆盖率指标可以考虑到外部库的代码路径。

Let’s look more closely at each of these reasons.

让我们更仔细地看看这些原因中的每一个。

#### [](#您无法保证测试验证所有可能的结果 "您无法保证测试验证所有可能的结果")您无法保证测试验证所有可能的结果

**YOU CAN’T GUARANTEE THAT THE TEST VERIFIES ALL THE POSSIBLE OUTCOMES**

For the code paths to be actually tested and not just exercised, your unit tests must have appropriate assertions. In other words, you need to check that the outcome the system under test produces is the exact outcome you expect it to produce. Moreover, this outcome may have several components; and for the coverage metrics to be meaningful, you need to verify all of them.

为了使代码路径真正被测试，而不仅仅是被执行，你的单元测试必须有适当的断言。换句话说，你需要检查被测系统产生的结果是否是你期望它产生的准确结果。此外，这个结果可能有几个组成部分；为了使覆盖率指标有意义，你需要验证所有的组成部分。

The next listing shows another version of the IsStringLong method. It records the last result into a public WasLastStringLong property.

下一个列表显示了 IsStringLong 方法的另一个版本。它将最后的结果记录在一个公共的 WasLastStringLong 属性中。

Listing 1.2 Version of IsStringLong that records the last result 清单1.2 记录最后结果的IsStringLong的版本

![image-20230409182053040](~/assets/images/unit-testing-1/image-20230409182053040.png)

The IsStringLong method now has two outcomes: an explicit one, which is encoded by the return value; and an implicit one, which is the new value of the property. And in spite of not verifying the second, implicit outcome, the coverage metrics would still show the same results: 100% for the code coverage and 50% for the branch coverage. As you can see, the coverage metrics don’t guarantee that the underlying code is tested, only that it has been executed at some point.

IsStringLong 方法现在有两个结果：一个是显式结果，由返回值编码；另一个是隐式结果，即属性的新值。尽管没有验证第二个隐式结果，但覆盖率指标仍然显示相同的结果： 代码覆盖率为100%，分支覆盖率为50%。正如你所看到的，覆盖率指标并不能保证底层代码被测试，只能保证它在某个时刻被执行过。

An extreme version of this situation with partially tested outcomes is assertion-free testing, which is when you write tests that don’t have any assertion statements in them whatsoever. Here’s an example of assertion-free testing.

这种部分测试结果的极端版本是无断言测试，即当你写的测试中没有任何断言语句。下面是一个无断言测试的例子。

Listing 1.3 A test with no assertions always passes. 清单1.3 一个没有断言的测试总是通过。

![image-20230409182127450](~/assets/images/unit-testing-1/image-20230409182127450.png)

This test has both code and branch coverage metrics showing 100%. But at the same time, it is completely useless because it doesn’t verify anything.

这个测试的代码和分支覆盖率指标都显示为100%。但与此同时，它完全没有用处，因为它没有验证任何东西。

> A story from the trenches 一个来自一线的故事
> 
> The concept of assertion-free testing might look like a dumb idea, but it does happen in the wild.
> 
> 无断言测试的概念可能看起来像是一个愚蠢的想法，但在实际中确实存在。
> 
> Years ago, I worked on a project where management imposed a strict requirement of having 100% code coverage for every project under development. This initiative had noble intentions. It was during the time when unit testing wasn’t as prevalent as it is today. Few people in the organization practiced it, and even fewer did unit testing consistently.
> 
> 几年前，我在一个项目中工作，管理层对每个正在开发的项目都提出了严格的要求，即100%的代码覆盖。这一举措的初衷很高尚。那是在单元测试还没有像今天这样普遍的时候。组织中很少有人进行单元测试，甚至很少有人持续进行单元测试。
> 
> A group of developers had gone to a conference where many talks were devoted to unit testing. After returning, they decided to put their new knowledge into practice. Upper management supported them, and the great conversion to better programming techniques began. Internal presentations were given. New tools were installed. And, more importantly, a new company-wide rule was imposed: all development teams had to focus on writing tests exclusively until they reached the 100% code coverage mark. After they reached this goal, any code check-in that lowered the metric had to be rejected by the build systems.
> 
> 一群开发人员去参加一个会议，会上有很多关于单元测试的讨论。回来后，他们决定将他们的新知识用于实践。上层管理人员支持他们，并开始了向更好的编程技术的伟大转换。内部演讲开始了。新的工具被安装。更重要的是，一个新的公司规则被强加于人：所有的开发团队都必须专注于编写测试，直到他们达到100%的代码覆盖率。在他们达到这个目标后，任何降低指标的代码检查都必须被构建系统拒绝。
> 
> As you might guess, this didn’t play out well. Crushed by this severe limitation, developers started to seek ways to game the system. Naturally, many of them came to the same realization: if you wrap all tests with try/catch blocks and don’t introduce any assertions in them, those tests are guaranteed to pass. People started to mindlessly create tests for the sake of meeting the mandatory 100% coverage requirement. Needless to say, those tests didn’t add any value to the projects. Moreover, they damaged the projects because of all the effort and time they steered away from productive activities, and because of the upkeep costs required to maintain the tests moving forward.
> 
> 正如你可能猜到的，这并没有取得好的效果。受到这一严重限制的打击，开发者们开始寻找绕过这个限制的方法。自然而然地，他们中的许多人得出了同样的结论：如果你用 try/catch 块包裹所有的测试并且不在其中引入任何断言，那么这些测试就会被保证通过。为了达到强制要求的100%覆盖率，人们开始盲目地创建测试。不用说，这些测试并没有给项目增加任何价值。更糟糕的是，它们因为耗费了本可以用于生产性活动的努力和时间，以及为了维护这些测试所需的持续成本而损害了项目。
> 
> Eventually, the requirement was lowered to 90% and then to 80%; after some period of time, it was retracted altogether (for the better!).
> 
> 最终，这个要求被降低到 90%，然后又降低到 80%；一段时间后，它被完全收回了（为了更好的发展！）。

But let’s say that you thoroughly verify each outcome of the code under test. Does this, in combination with the branch coverage metric, provide a reliable mechanism, which you can use to determine the quality of your test suite? Unfortunately, no.

但是，假设你彻底验证了被测试代码的每个结果。这与分支覆盖率指标相结合，是否提供了一个可靠的机制，让你可以用它来确定你的测试套件的质量？不幸的是，没有。

#### [](#没有任何覆盖率指标能够考虑到外部库中的代码路径 "没有任何覆盖率指标能够考虑到外部库中的代码路径")没有任何覆盖率指标能够考虑到外部库中的代码路径

**NO COVERAGE METRIC CAN TAKE INTO ACCOUNT CODE PATHS IN EXTERNAL LIBRARIES**

The second problem with all coverage metrics is that they don’t take into account code paths that external libraries go through when the system under test calls methods on them. Let’s take the following example:

所有覆盖率指标的第二个问题是，它们没有考虑到被测系统调用外部库的方法时所经过的代码路径。让我们来看看下面的例子：

![image-20230409182247982](~/assets/images/unit-testing-1/image-20230409182247982.png)

The branch coverage metric shows 100%, and the test verifies all components of the method’s outcome. It has a single such component anyway—the return value. At the same time, this test is nowhere near being exhaustive. It doesn’t take into account the code paths the .NET Framework’s int.Parse method may go through. And there are quite a number of code paths, even in this simple method, as you can see in figure 1.6.

分支覆盖率指标显示为 100%，测试验证了该方法结果的所有组成部分。反正它有一个这样的组件–返回值。同时，这个测试还远远没有达到详尽的程度。它没有考虑到 .NET 框架的 int.Parse 方法可能经过的代码路径。正如你在图1.6中看到的，即使在这个简单的方法中，也有相当多的代码路径。

![image-20230409182304241](~/assets/images/unit-testing-1/image-20230409182304241.png)

Figure 1.6 Hidden code paths of external libraries. Coverage metrics have no way to see how many of them there are and how many of them your tests exercise.

图1.6 外部库的隐藏代码路径。覆盖率指标没有办法看到其中有多少条，以及你的测试行使了多少条。

The built-in integer type has plenty of branches that are hidden from the test and that might lead to different results, should you change the method’s input parameter. Here are just a few possible arguments that can’t be transformed into an integer:

内置的整数类型有很多分支被隐藏在测试中，如果你改变了方法的输入参数，可能会导致不同的结果。下面是一些不能转化为整数的可能参数：

*   Null value
*   An empty string
*   “Not an int”
*   A string that’s too large

You can fall into numerous edge cases, and there’s no way to see if your tests account for all of them.

你可能会陷入许多边界条件，而且没有办法看到你的测试是否考虑到了所有这些情况。

This is not to say that coverage metrics should take into account code paths in external libraries (they shouldn’t), but rather to show you that you can’t rely on those metrics to see how good or bad your unit tests are. Coverage metrics can’t possibly tell whether your tests are exhaustive; nor can they say if you have enough tests.

这并不是说覆盖率指标应该考虑外部库中的代码路径（它们不应该），而是要告诉你，你不能依靠这些指标来了解你的单元测试的好坏程度。覆盖率指标不可能告诉你的测试是否详尽；也不可能告诉你是否有足够的测试。

### [](#1-3-4-瞄准特定的覆盖率数字 "1.3.4 瞄准特定的覆盖率数字")1.3.4 瞄准特定的覆盖率数字

**Aiming at a particular coverage number**

At this point, I hope you can see that relying on coverage metrics to determine the quality of your test suite is not enough. It can also lead to dangerous territory if you start making a specific coverage number a target, be it 100%, 90%, or even a moderate 70%. The best way to view a coverage metric is as an indicator, not a goal in and of itself.

在这一点上，我希望你能看到，依靠覆盖率指标来确定你的测试套件的质量是不够的。如果你开始把一个特定的覆盖率数字作为目标，无论是100%，90%，甚至是适度的70%，它也会导致危险的领域。查看覆盖率指标的最好方法是作为一个指标，而不是目标本身。

Think of a patient in a hospital. Their high temperature might indicate a fever and is a helpful observation. But the hospital shouldn’t make the proper temperature of this patient a goal to target by any means necessary. Otherwise, the hospital might end up with the quick and “efficient” solution of installing an air conditioner next to the patient and regulating their temperature by adjusting the amount of cold air flowing onto their skin. Of course, this approach doesn’t make any sense.

想想医院里的病人。他们的高体温可能表明发烧，是一个有用的观察。但医院不应该把这个病人的适当体温作为目标，不择手段地去实现。否则，医院最终可能会采用快速和 “有效 “的解决方案，在病人旁边安装一个空调，通过调整流向他们皮肤的冷空气量来调节他们的温度。当然，这种方法没有任何意义。

Likewise, targeting a specific coverage number creates a perverse incentive that goes against the goal of unit testing. Instead of focusing on testing the things that matter, people start to seek ways to attain this artificial target. Proper unit testing is difficult enough already. Imposing a mandatory coverage number only distracts developers from being mindful about what they test, and makes proper unit testing even harder to achieve.

同样，以特定的覆盖率为目标会产生一种不正当的激励，与单元测试的目标背道而驰。人们不是专注于测试那些重要的东西，而是开始寻求达到这个人为目标的方法。正确的单元测试已经很困难了。强加一个强制性的覆盖率数字只会分散开发人员的注意力，使他们不注意测试的内容，并使正确的单元测试更难实现。

> TIP
> 
> It’s good to have a high level of coverage in core parts of your system. It’s bad to make this high level a requirement. The difference is subtle but critical.
> 
> 在系统的核心部分拥有高水平的覆盖率是件好事。但把这种高水平作为一种要求就不好了。这之间的区别很微妙，但很关键。

Let me repeat myself: coverage metrics are a good negative indicator, but a bad positive one. Low coverage numbers—say, below 60%—are a certain sign of trouble. They mean there’s a lot of untested code in your code base. But high numbers don’t mean anything. Thus, measuring the code coverage should be only a first step on the way to a quality test suite.

让我重复一遍：覆盖率指标是一个好的负面指标，但作为一个正面指标却很差。低覆盖率——比如说，低于60%——肯定是存在问题的迹象。这意味着你的代码库中有大量的未经过测试的代码。但是高覆盖率数字并不代表什么。因此，测量代码覆盖率应该只是通往高质量测试套件的第一步。

## [](#1-4-什么样的测试套件是成功的？ "1.4 什么样的测试套件是成功的？")1.4 什么样的测试套件是成功的？

**What makes a successful test suite?**

I’ve spent most of this chapter discussing improper ways to measure the quality of a test suite: using coverage metrics. What about a proper way? How should you measure your test suite’s quality? The only reliable way is to evaluate each test in the suite individually, one by one. Of course, you don’t have to evaluate all of them at once; that could be quite a large undertaking and require significant upfront effort. You can perform this evaluation gradually. The point is that there’s no automated way to see how good your test suite is. You have to apply your personal judgment.

本章大部分时间我都在讨论度量测试套件质量的不恰当方法：使用覆盖率指标。那么正确的方法是什么呢？你应该如何度量你的测试套件的质量？唯一可靠的方法是对套件中的每个测试逐一进行评估。当然，你不必一次评估所有的测试；这可能是一个相当大的工程，需要大量的前期工作。你可以逐步进行这种评估。问题是，没有自动化的方法可以看到你的测试套件有多好。你必须运用你的个人判断。

Let’s look at a broader picture of what makes a test suite successful as a whole. (We’ll dive into the specifics of differentiating between good and bad tests in chapter 4.) A successful test suite has the following properties:

让我们来看看使一个测试套件整体上获得成功的更广泛的图景。（我们将在第四章中深入探讨区分好测试和坏测试的具体细节。）一个成功的测试套套件具有以下特性：

*   It’s integrated into the development cycle. 它被集成到开发周期中。
    
*   It targets only the most important parts of your code base. 它只针对你的代码库中最重要的部分。
    
*   It provides maximum value with minimum maintenance costs. 它以最小的维护成本提供最大的价值。
    

### [](#1-4-1-它被集成到开发周期中 "1.4.1 它被集成到开发周期中")1.4.1 它被集成到开发周期中

**It’s integrated into the development cycle**

The only point in having automated tests is if you constantly use them. All tests should be integrated into the development cycle. Ideally, you should execute them on every code change, even the smallest one.

拥有自动化测试的唯一意义在于你不断地使用它们。所有的测试应该被整合到开发周期中。理想情况下，你应该在每一个代码变更上执行它们，即使是最小的变更。

### [](#1-4-2-它只针对你的代码库中最重要的部分 "1.4.2 它只针对你的代码库中最重要的部分")1.4.2 它只针对你的代码库中最重要的部分

**It targets only the most important parts of your code base**

Just as all tests are not created equal, not all parts of your code base are worth the same attention in terms of unit testing. The value the tests provide is not only in how those tests themselves are structured, but also in the code they verify.

正如所有的测试都是不一样的，在单元测试方面，不是所有的代码库部分都值得同样的关注。测试提供的价值不仅体现在这些测试本身的结构上，也体现在它们所验证的代码上。

It’s important to direct your unit testing efforts to the most critical parts of the system and verify the others only briefly or indirectly. In most applications, the most important part is the part that contains business logic—the domain model.【1】 Testing business logic gives you the best return on your time investment.

重要的是，将你的单元测试工作引向系统中最关键的部分，而对其他部分只进行简单的或间接的验证。在大多数应用程序中，最重要的部分是包含业务逻辑的部分–领域模型。测试业务逻辑可以使你的时间投资得到最好的回报。

All other parts can be divided into three categories:

所有其他部分可以分为三类：

*   Infrastructure code 基础设施代码
*   External services and dependencies, such as the database and third-party systems 外部服务和依赖，如数据库和第三方系统
*   Code that glues everything together 将所有东西粘在一起的代码

Some of these other parts may still need thorough unit testing, though. For example, the infrastructure code may contain complex and important algorithms, so it would make sense to cover them with a lot of tests, too. But in general, most of your attention should be spent on the domain model.

不过，这些其他部分中的一些可能仍然需要彻底的单元测试。例如，基础设施代码可能包含复杂而重要的算法，所以用大量的测试覆盖它们也是有意义的。但一般来说，你的大部分注意力应该花在领域模型上。

Some of your tests, such as integration tests, can go beyond the domain model and verify how the system works as a whole, including the noncritical parts of the code base. And that’s fine. But the focus should remain on the domain model.

你们的一些测试，比如集成测试，可以超出领域模型的范围，验证系统的整体工作情况，包括代码库中非关键的部分。这是可以的。但焦点仍然应该放在领域模型上。

Note that in order to follow this guideline, you should isolate the domain model from the non-essential parts of the code base. You have to keep the domain model separated from all other application concerns so you can focus your unit testing efforts on that domain model exclusively. We talk about all this in detail in part 2 of the book.

请注意，为了遵循这一准则，你应该将领域模型与代码库的非关键部分隔离。你必须把领域模型与所有其他应用程序的关注点分开，这样你就可以把你的单元测试工作完全集中在这个领域模型上。我们在本书的第二部分中详细讨论了这一切。

^1 See Domain-Driven Design: Tackling Complexity in the Heart of Software by Eric Evans (Addison-Wesley, 2003).

### [](#1-4-3-它以最小的维护成本提供最大的价值 "1.4.3 它以最小的维护成本提供最大的价值")1.4.3 它以最小的维护成本提供最大的价值

**It provides maximum value with minimum maintenance costs**

The most difficult part of unit testing is achieving maximum value with minimum maintenance costs. That’s the main focus of this book.

单元测试中最困难的部分是以最小的维护成本实现最大的价值。这也是本书的重点。

It’s not enough to incorporate tests into a build system, and it’s not enough to maintain high test coverage of the domain model. It’s also crucial to keep in the suite only the tests whose value exceeds their upkeep costs by a good margin.

仅仅将测试纳入构建系统是不够的，仅仅保持领域模型的高测试覆盖率也是不够的。同样重要的是，在套件中只保留那些价值超过其维护成本的测试。

This last attribute can be divided in two:

这最后一个属性可以一分为二：

*   Recognizing a valuable test (and, by extension, a test of low value) 识别一个有价值的测试（以及延伸到一个低价值的测试）。
*   Writing a valuable test 编写一个有价值的测试

Although these skills may seem similar, they’re different by nature. To recognize a test of high value, you need a frame of reference. On the other hand, writing a valuable test requires you to also know code design techniques. Unit tests and the underlying code are highly intertwined, and it’s impossible to create valuable tests without putting significant effort into the code base they cover.

尽管这些技能看起来很相似，但它们在本质上是不同的。要识别一个高价值的测试，你需要一个参考框架。另一方面，写一个有价值的测试需要你也知道代码设计技术。单元测试和底层代码是高度交织在一起的，如果不在其覆盖的代码基础上投入大量精力，就不可能创造出有价值的测试。

You can view it as the difference between recognizing a good song and being able to compose one. The amount of effort required to become a composer is asymmetrically larger than the effort required to differentiate between good and bad music. The same is true for unit tests. Writing a new test requires more effort than examining an existing one, mostly because you don’t write tests in a vacuum: you have to take into account the underlying code. And so although I focus on unit tests, I also devote a significant portion of this book to discussing code design.

你可以将其看作是识别一首好歌和能够创作一首歌之间的区别。成为一名作曲家所需的努力远远大于区分好音乐和坏音乐所需的努力。单元测试也是如此。编写一个新的测试比检查一个现有的测试需要更多的努力，主要是因为你在编写测试时不是孤立进行的：你需要考虑底层的代码。因此，尽管我主要关注单元测试，但我也在这本书中大量讨论了代码设计。

## [](#1-5-在本书中你将学到的内容 "1.5 在本书中你将学到的内容")1.5 在本书中你将学到的内容

**What you will learn in this book**

This book teaches a frame of reference that you can use to analyze any test in your test suite. This frame of reference is foundational. After learning it, you’ll be able to look at many of your tests in a new light and see which of them contribute to the project and which must be refactored or gotten rid of altogether.

本书讲授了一个参考框架，你可以用它来分析你的测试套件中的任何测试。这个参考框架是基础性的。在学习了它之后，你将能够以一种新的眼光来看待你的许多测试，看看它们中哪些对项目有贡献，哪些必须重构或完全摆脱。

After setting this stage (chapter 4), the book analyzes the existing unit testing techniques and practices (chapters 4–6, and part of 7). It doesn’t matter whether you’re familiar with those techniques and practices. If you are familiar with them, you’ll see them from a new angle. Most likely, you already get them at the intuitive level. This book can help you articulate why the techniques and best practices you’ve been using all along are so helpful.

在设定好这个前提后（第四章），本书将分析现有的单元测试技术和实践（第四到第六章，以及第七章的一部分）。无论你是否熟悉这些技术和实践都没有关系。如果你已经熟悉它们，你会从一个新的角度来审视它们。很可能，你已经在直觉层面上掌握了它们。这本书可以帮助你阐明为什么你一直以来使用的这些技术和最佳实践如此有帮助。

Don’t underestimate this skill. The ability to clearly communicate your ideas to colleagues is priceless. A software developer—even a great one—rarely gets full credit for a design decision if they can’t explain why, exactly, that decision was made. This book can help you transform your knowledge from the realm of the unconscious to something you are able to talk about with anyone.

不要低估这项技能。向同事清楚地传达你的想法的能力是无价的。一个软件开发者–即使是一个伟大的开发者–如果不能准确地解释为什么会做出这样的决定，也很难得到设计决定的充分肯定。这本书可以帮助你将你的知识从无意识的领域转化为你能够与任何人谈论的东西。

If you don’t have much experience with unit testing techniques and best practices, you’ll learn a lot. In addition to the frame of reference that you can use to analyze any test in a test suite, the book teaches

如果你对单元测试技术和最佳实践没有什么经验，你会学到很多东西。除了你可以用来分析测试套件中的任何测试的参考框架外，本书还教给你

*   How to refactor the test suite along with the production code it covers 如何将测试套件与它所涵盖的生产代码一起重构
*   How to apply different styles of unit testing 如何应用不同风格的单元测试
*   Using integration tests to verify the behavior of the system as a whole 使用集成测试来验证整个系统的行为
*   Identifying and avoiding anti-patterns in unit tests 识别和避免单元测试中的反模式

In addition to unit tests, this book covers the entire topic of automated testing, so you’ll also learn about integration and end-to-end tests.

除了单元测试，本书还涵盖了自动化测试的整个主题，所以你还会学到集成和端到端测试。

I use C# and .NET in my code samples, but you don’t have to be a C# professional to read this book; C# is just the language that I happen to work with the most. All the concepts I talk about are non-language-specific and can be applied to any other object-oriented language, such as Java or C++.

我在代码样本中使用了 C# 和 .NET，但你不必是 C# 专业人员来阅读本书；C# 只是我碰巧使用最多的一种语言。我谈论的所有概念都是非特定语言的，可以应用于任何其他面向对象的语言，如 Java 或 C++。

## [](#1-6-总结 "1.6 总结")1.6 总结

**Summary**

*   Code tends to deteriorate. Each time you change something in a code base, the amount of disorder in it, or entropy, increases. Without proper care, such as constant cleaning and refactoring, the system becomes increasingly complex and disorganized. Tests help overturn this tendency. They act as a safety net— a tool that provides insurance against the vast majority of regressions. 代码倾向于恶化。每当你改变代码库中的某些东西时，其中的无序程度或熵就会增加。如果没有适当的照顾，例如不断的清理和重构，系统会变得越来越复杂和无序。测试有助于扭转这种趋势。他们充当了一个安全网–一个提供保险的工具，以防止绝大多数的回归。
*   It’s important to write unit tests. It’s equally important to write good unit tests. The end result for projects with bad tests or no tests is the same: either stagnation or a lot of regressions with every new release. 写单元测试很重要。同样重要的是写好单元测试。糟糕的测试或没有测试的项目的最终结果是相同的：要么停滞不前，要么在每个新版本中出现大量的回归。
*   The goal of unit testing is to enable sustainable growth of the software project. A good unit test suite helps avoid the stagnation phase and maintain the development pace over time. With such a suite, you’re confident that your changes won’t lead to regressions. This, in turn, makes it easier to refactor the code or add new features. 单元测试的目标是实现软件项目的可持续增长。一个好的单元测试套件有助于避免停滞阶段，并随着时间的推移保持开发速度。有了这样一个套件，你就有信心你的改变不会导致回归。这反过来又使重构代码或添加新功能变得更加容易。
*   All tests are not created equal. Each test has a cost and a benefit component, and you need to carefully weigh one against the other. Keep only tests of positive net value in the suite, and get rid of all others. Both the application code and the test code are liabilities, not assets. 所有的测试都是不一样的。每个测试都有一个成本和收益部分，你需要仔细权衡其中的一个。在测试套件中只保留净值为正的测试，而去掉所有其他测试。应用程序代码和测试代码都是负债，而不是资产。
*   The ability to unit test code is a good litmus test, but it only works in one direction. It’s a good negative indicator (if you can’t unit test the code, it’s of poor quality) but a bad positive one (the ability to unit test the code doesn’t guarantee its quality). 能够对代码进行单元测试是一个很好的试金石，但它只在一个方向上有效。它是一个好的负面指标（如果你无法对代码进行单元测试，那么代码的质量较差），但却不是一个好的正面指标（能够对代码进行单元测试并不能保证代码的质量）。
*   Likewise, coverage metrics are a good negative indicator but a bad positive one. Low coverage numbers are a certain sign of trouble, but a high coverage number doesn’t automatically mean your test suite is of high quality. 同样，覆盖率指标是一个好的负面指标，但不是一个好的正面指标。低覆盖率数字肯定是存在问题的迹象，但高覆盖率数字并不自动意味着你的测试套件质量高。
*   Branch coverage provides better insight into the completeness of the test suite but still can’t indicate whether the suite is good enough. It doesn’t take into account the presence of assertions, and it can’t account for code paths in thirdparty libraries that your code base uses. 分支覆盖率可以更好地了解测试套件的完整性，但仍然不能说明该套件是否足够好。它没有考虑到断言的存在，也没有考虑到你的代码库中使用的第三方库的代码路径。
*   Imposing a particular coverage number creates a perverse incentive. It’s good to have a high level of coverage in core parts of your system, but it’s bad to make this high level a requirement. 强制要求特定的覆盖率会产生一种扭曲的激励。在系统的核心部分拥有高覆盖率是好的，但将这种高水平的覆盖率作为硬性要求则是不好的。
*   A successful test suite exhibits the following attributes: 一个成功的测试套件具有以下特征：
    *   – It is integrated into the development cycle. 它被整合到开发周期中
    *   It targets only the most important parts of your code base. 它只针对你的代码库中最重要的部分
    *   It provides maximum value with minimum maintenance costs. 它以最小的维护成本提供最大的价值
*   The only way to achieve the goal of unit testing (that is, enabling sustainable project growth) is to 使其更有价值实现单元测试目标的唯一方法（即实现项目的可持续增长）是
    *   Learn how to differentiate between a good and a bad test. 学会如何区分好的和坏的测试
    *   Be able to refactor a test to make it more valuable. 能够重构一个测试