# Task 2 - Rubric Changes and Manual Scores

**Inputs:** the five Homework 4 outputs (accepted prompt, Iteration 1) and the unaltered ticket `Body` from the canonical dataset. The rubric is in `rubric_frozen.md`. Scale for every score: 0, 0.5, or 1.

All five outputs are valid JSON, so the gate does not apply.

## Rubric changes

I scored the tickets with version 1. Four rules were too vague to give one clear answer. I changed them, then re-scored.

### Request coverage

**Version 1:** 0.5 means "one other ask is missing."

**Version 2:** 0.5 means the main ask is present and at least half of all asks are present. 0 means fewer than half. The scorer lists and counts the asks.

**Why:** Tickets 28907 (2 of 5 asks missing), 28571 (3 of 6 missing), and 29206 (3 of 9 missing) fit no row.

**Score effect:** None after the rule. Before it, these three had no valid score.

### Missing information

**Version 1:** "a gap is clear."

**Version 2:** A clear gap is a fact the agent needs in order to act that the body lacks. The scorer must name it. Placeholders (`acc_num`, `tel_num`) never count.

**Why:** "Clear" was a feeling. A named fact makes it checkable.

**Score effect:** None. Every 0.5 below now names its gap.

### Summary job

**Version 1:** 0.5 for "copies the request" or "drops a tried step."

**Version 2:** Restating the request without the problem also scores 0.5. A tried step is something the customer did to fix or check the problem. An audit finding is part of the issue.

**Why:** 28921 states a wish, not a problem. 28907's audit was unclear.

**Score effect:** 28907 moved from 0.5 to 1. 28921 was undecided between 0 and 0.5, and is now 0.5.

### Grounded

**Version 1:** "Every statement is in the body."

**Version 2:** This dimension judges only what is written. Omissions belong to Request coverage, Missing information, and Summary job.

**Why:** Dropped details were punished twice.

**Score effect:** None.

## 28907 Billing and Payments

### Body

Dear Customer Support Team, I hope this message finds you well. I am reaching out to request assistance with a billing adjustment related to our recent usage of the AWS Management Service, provided through your esteemed IT Services company. I represent Company and we have an account under the number acc_num that is associated with our ongoing AWS infrastructure operations. Upon reviewing our usage and subsequent billing statement for the last quarter, we noticed certain discrepancies which we would like to clarify. For the duration of the last quarter, our AWS Management Service was utilized to enhance various aspects of our operational infrastructure, yet the billing seems higher than initially anticipated. What I'd appreciate is a comprehensive review of the charges linked to our account. Specifically, the billing reflects charges that were not discussed or predicted in our previous correspondence regarding expected usage rates and associated expenses. My team conducted an internal audit and found differences in the projections versus the billed amounts in the billing documentation provided by you on date. It would be extremely beneficial if we could arrange a detailed breakdown of the billed items, accompanied by detailed usage metrics, and a written explanation for each charge where discrepancies have been noted. Additionally, I would like to inquire if there are any ongoing discounts or billing mechanisms that would better suit our usage patterns but were not applied to our account. Your guidance on any available options for invoicing adjustments under the current service agreement would be much appreciated. For quick resolution of this matter, I am available for further discussions at your earliest convenience. Please feel free to reach out to me directly via email or at my phone number, tel_num, anytime during business hours. Alternatively, my colleague name can be contacted in my absence for any clarifications needed. Thank you in advance for your attention to this matter. I anticipate your insights and hope to resolve this discrepancy in a timely fashion. Looking forward to your prompt response. Kind regards, name Position Company Address Contact Information

### Output

- **summary:** Billing discrepancy for AWS Management Service usage and expected charges.
- **customer_request:** Request for a comprehensive review of the charges linked to the account, detailed breakdown of billed items, usage metrics, and a written explanation for discrepancies noted.
- **missing_information:** []

### Grounded

**Score: 1.** The summary and the request match the body. The body says "the billing seems higher than initially anticipated", "a comprehensive review of the charges", "detailed usage metrics", and "a written explanation for each charge".

### Request coverage

**Score: 0.5.** The body has 5 asks: a review of the charges, an itemized breakdown with usage metrics, a written explanation, discounts that were not applied, and invoice adjustment options. The output has the first three (3 of 5, and the main ask is present). It drops the discounts question and the adjustment options.

### Missing information

**Score: 0.5.** The list is empty. The body gives no billed amount, no expected amount, and no name for the charges in dispute. Those are the facts an agent needs before acting. `acc_num`, `tel_num`, and `name` are placeholders, so they do not count.

### Summary job

**Score: 1.** "Billing discrepancy for AWS Management Service usage and expected charges." One sentence. The product and the problem are clear, and the sentence is different from the request. The internal audit is part of the issue: the team found differences between projections and billed amounts.

**Total: 3.0 of 4.**

## 28921 Human Resources

### Body

Dear IT Services Customer Support, I am writing to request a significant enhancement to our internal human resources management system, specifically targeting the user interface design and data analysis capabilities. Despite the comprehensive functions that your system currently offers, we believe improvements can be made to enhance user experience and provide more intuitive data handling processes for our team. Our personnel have reported some challenges when navigating through various modules and accessing crucial information, which often results in bottlenecks and decreased efficiency. A redesigned interface that is more user-friendly and visually intuitive could significantly aid in quicker data entry and easier retrieval of information. Furthermore, implementing advanced data analysis tools would allow our HR team to perform more detailed assessments and generate reports with greater ease. While the IT Consulting Service has offered us fantastic support so far, these enhancements could drive even greater value, facilitating smoother organizational workflows and fostering data-driven decision-making across different teams. Please treat this request with urgency, as optimizing these elements is essential to meet our evolving business needs. If possible, we would appreciate receiving information on your plan for tackling this request, including a timeline for implementation. Thank you for your prompt attention to this matter. Should you need any additional information, please do not hesitate to contact me directly at tel_num. I look forward to your response and the ongoing improvement of our HR management system. Sincerely, name name Corp Account Number: acc_num

### Output

- **summary:** Request for enhanced user interface and data analysis capabilities in the internal human resources management system.
- **customer_request:** Request for a redesigned user interface that is more intuitive and visually appealing, and for advanced data analysis tools to improve data handling processes and facilitate smoother organizational workflows.
- **missing_information:** []

### Grounded

**Score: 0.5.** The body says "user-friendly and visually intuitive". The output says "more intuitive and visually appealing". One word shifted. The case stays the same: a clearer HR screen.

### Request coverage

**Score: 0.5.** The body has 3 asks: a redesigned interface, advanced data analysis tools, and a plan with a timeline. The output has the first two (2 of 3). The plan and the timeline are missing.

### Missing information

**Score: 0.5.** The list is empty. The body never says which modules are hard to navigate, and it never says which reports are wanted. An agent cannot start the redesign from the body alone. `tel_num` and `acc_num` are placeholders.

### Summary job

**Score: 0.5.** "Request for enhanced user interface and data analysis capabilities" states a wish. It leaves out the problem in the body: staff struggle to find information, and that causes bottlenecks.

**Total: 2.0 of 4.**

## 28763 Product Support

### Body

Dear Customer Support Team, I hope this message finds you well. I am writing to report a concerning issue I am experiencing with my recently purchased Samsung QLED QN90A TV, which I bought from your 'Tech Online Store'. Having been a loyal customer, I expected nothing short of superior performance and reliability that Samsung products are renowned for. However, this particular unit seems to be presenting a rather persistent and distracting problem. The television has developed a flickering issue while in use, which occurs intermittently but frequently enough to hinder the viewing experience significantly. It started subtly but has become more pronounced over time, leading me to believe that it might be a hardware-related issue rather than something that could be adjusted with simple settings modifications. I understand these models are generally known for their impressive picture quality and advanced technology, so this flickering is both unexpected and disappointing. Given the nature of the problem, I suspect it might involve components relating to the display hardware, as no changes in external settings such as cables or power sources appear to affect or resolve the issue. Unfortunately, adjusting brightness levels or refreshing the support software has shown no improvement. Considering these attempts to troubleshoot the problem have been unsuccessful, I am compelled to seek your professional assistance to resolve this matter promptly. I would appreciate it if you could provide guidance on the next steps to take, possibly including instructions for an at-home diagnosis or arranging a qualified technician's assessment. Additionally, information about your repair policies and warranty coverage for such issues would be greatly appreciated. My hope is to have this resolved quickly to return to enjoying the high-quality viewing experience I anticipated upon purchase. Thank you for your attention to this matter. I look forward to your prompt response with advice on how we can proceed to rectify this issue with my Samsung QLED QN90A. Best regards, name acc_num

### Output

- **summary:** Samsung QLED QN90A TV flickering issue reported by customer.
- **customer_request:** Reported issue: Samsung QLED QN90A TV flickering issue. The customer is seeking professional assistance to resolve the problem. They are also requesting guidance on the next steps and information about repair policies and warranty coverage.
- **missing_information:** []

### Grounded

**Score: 1.** "Samsung QLED QN90A", "flickering", and "repair policies and warranty coverage" are all in the body.

### Request coverage

**Score: 1.** The body asks for next-step guidance, including an at-home diagnosis or a technician, and for repair policy and warranty information. The output has "guidance on the next steps" and "repair policies and warranty coverage".

### Missing information

**Score: 0.5.** The list is empty. The body gives no purchase date and no order number, so warranty status cannot be checked. `name` and `acc_num` are placeholders.

### Summary job

**Score: 0.5.** The summary names the product and the flicker. It leaves out the tried steps in the body: cables and power were checked, brightness was changed, and the software was refreshed. Nothing helped.

**Total: 3.0 of 4.**

## 28571 Sales and Pre-Sales

### Body

Dear Customer Support, I hope this message finds you well. I am reaching out to obtain some clarifications regarding specific information and shipping options for the Cisco Router ISR4331, as I am considering it for a possible acquisition. It is important for me to verify that this model suits my requirements, so I would be thankful for expanded details about its technical specifications, particularly in terms of its effectiveness, compatibility, and any unique features it possesses. In addition, a key aspect of my inquiry pertains to the delivery timeline. As you may recognize, receiving the product promptly is essential for the current schedule of our project. Could you please furnish detailed information covering the following aspects: expected delivery time from the order date, choice of shipping methods, and whether there are any expedited service options available? Furthermore, will it be possible to track the package once it has been dispatched? Your information regarding expected durations for both regular and faster service would be highly beneficial. Lastly, I would appreciate details on the return policy in case the product does not meet our expectations. Understanding your support protocols for these situations is vital for fostering trust as we consider moving forward with this purchase. A prompt response would be invaluable, greatly aiding me in my decision-making. You can reach me at this email or by phone at tel_num during regular working hours. Thank you for your assistance. Kind regards, name

### Output

- **summary:** Customer is seeking clarification on technical specifications, delivery timeline, and return policy for the Cisco Router ISR4331.
- **customer_request:** Clarification on technical specifications, delivery timeline, and return policy for the Cisco Router ISR4331.
- **missing_information:** []

### Grounded

**Score: 1.** "technical specifications", "delivery timeline", "return policy", and "Cisco Router ISR4331" are in the body.

### Request coverage

**Score: 0.5.** The body has 6 asks: specifications, delivery time, shipping methods, expedited options, tracking, and the return policy. The output covers specifications, delivery, and the return policy (3 of 6). Shipping methods, expedited service, and tracking are gone.

### Missing information

**Score: 0.5.** The list is empty. The body gives no quantity, no delivery destination, and no needed-by date. `tel_num` and `name` are placeholders.

### Summary job

**Score: 0.5.** The summary and the request are almost the same sentence. The summary does not say that the customer is deciding on a purchase for a project with a tight schedule.

**Total: 2.5 of 4.**

## 29206 Technical Support

### Body

Dear Customer Support Team, I hope this message finds you well. I am reaching out on behalf of our team at company_name. We have been utilizing Jira Software 8.20 as an essential tool for managing our project workflows, and it has significantly enhanced our productivity and project management capabilities. However, due to recent changes in our internal company policies, we require modifications to our existing workflows to better accommodate the new guidelines regarding ticket prioritization. In line with our new company policies, we need the ability to adjust the prioritization settings within Jira to reflect the changes in how issues should be processed and managed. Specifically, we are looking to incorporate a customized priority field that aligns with our updated prioritization matrix. Additionally, we would like to implement a feature that allows for dynamic adjustments based on the real-time status of issues and overarching project goals. Our objective is to ensure that our projects are managed more efficiently by allowing team members to categorize issues with the appropriate level of urgency as dictated by our new policy framework. Thus, we foresee the need for creating new custom workflows or modifying existing ones to include additional statuses and transition conditions which can accurately reflect these prioritization strategies. Could you please provide guidance on the best approach for implementing these workflow modifications? We are particularly interested in understanding the technical feasibility, potential timelines, and any assistance you can provide in terms of configuration or necessary plugins which might need to be applied to support these changes. It would be extremely helpful to have any documentation or best practices from prior similar implementations to help us navigate this adjustment seamlessly. We appreciate your attention to this matter and are hopeful for your expert advice on how to move forward. Please let us know a suitable time for us to discuss this in greater detail or if there are any initial resources you could provide to kickstart this process. Thank you very much for your support. Best regards, name position, company_name email_address tel_num

### Output

- **summary:** Need guidance on implementing workflow modifications to accommodate new company policies regarding ticket prioritization in Jira Software.
- **customer_request:** We need to modify our existing workflows to incorporate a customized priority field and a feature for dynamic adjustments based on real-time status and project goals. We are looking for technical feasibility, timelines, and assistance in configuration or necessary plugins to support these changes.
- **missing_information:** []

### Grounded

**Score: 1.** Every statement in the output is in the body. Dropping "8.20" is an omission. This dimension scores what was written, so that drop is not a Grounded miss.

### Request coverage

**Score: 0.5.** The body has 9 asks: a custom priority field, dynamic adjustment, new or changed workflows, guidance on the best approach, feasibility, timelines, configuration or plugin help, documentation and best practices, and a time to talk. The output has 6: the priority field, dynamic adjustment, workflow changes, feasibility, timelines, and plugins. Documentation, best practices, and the meeting are missing.

### Missing information

**Score: 0.5.** The list is empty. The body mentions an "updated prioritization matrix" and never describes it: no levels, no names. `company_name`, `email_address`, and `tel_num` are placeholders.

### Summary job

**Score: 1.** "Need guidance on implementing workflow modifications to accommodate new company policies regarding ticket prioritization in Jira Software." The problem and the product are clear, and the sentence differs from the request.

**Total: 3.0 of 4.**

## What these scores tell us

Missing information is the weakest dimension. It is 0.5 on all five tickets. The prompt never made the model list what is absent.

Request coverage is next. The five scores are 0.5, 0.5, 1, 0.5, and 0.5, so the average is 0.60. The model keeps the first asks and drops the later ones.

Grounded averages 0.90. Summary job averages 0.70. The five totals average 2.70 out of 4.

The rubric is frozen. Task 7 uses these scores as the no-RAG baseline.
