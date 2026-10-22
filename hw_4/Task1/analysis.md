## Slice selection ##
**Recommended choice**: true label *Technical Support*, predicted *IT Support*
**Rationale**:
- It is the **largest** count between true label and predicted label **confusion** (159 tickets), it is above 30 required.
- Since both of them are big (**big slices**), I can consider them as samples. Because its confusion is like a pair.
- Both departments shared vocabulary (software, access, etc.). It can be used to analyze the tickets text and to improve.
#### Records in Slice: 159
#### True Labels: 1095 As Technical Support
#### SHARE OF ALL VALIDATION ERROR: 0.08
- If we invert the TRUE_LABEL = IT Support Support and the PREDICTED_LABEL = Technical Support then the incorrect_count decreases to 107. 

## Selecting 30 records ##
- The fixed rule will get the same 30 tickets from the prediction file. 
** Explanation **:
1. TRUE_LABEL = "Technical Suport" and PREDICTED_DEPARTMENT = " IT Support"
2. Get only incorrect predictions where TRUE_LABEL != PREDICTED_DEPARTMENT
3. sort by `ticket_id`.
4. Get the first 30 rows.

## TICKETS' EVIDENCE ##

### Ticket findings

#### Ticket 54
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: The ticket says Outlook, email and network equipment are not responding. The strongest words are about the network and device failures.
- Why the model chose IT Support: The gap is small (0.025). 'network' (+0.175), 'malfunctions' (+0.120) and 'outlook' (+0.097) push to IT Support. The words for Technical Support are weak ('include' -0.081, 'device' -0.065).

#### Ticket 432
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: Connection and sync failures across hardware after a firmware upgrade and network changes. The words are about the network and devices.
- Why the model chose IT Support: The gap is tiny (0.021). 'upgrade' (+0.125), 'network' (+0.120) and 'suspected that' (+0.111) push to IT Support. 'firmware' (-0.101) pushes the other way but loses.

#### Ticket 460
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: A home irrigation device keeps disconnecting. It is a device problem, but the customer mentions the network connection, so network words show up.
- Why the model chose IT Support: 'network' (+0.113), 'facing difficulties' (+0.071) and 'the network' (+0.065) push to IT Support. 'the device' (-0.085) and 'device' (-0.084) push to Technical Support, but not enough (gap 0.061).

#### Ticket 820
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Very short ticket
- Why this category: The ticket is one sentence: 102 characters and 21 words the model knows. There is not enough text to tell the departments apart.
- Why the model chose IT Support: A few words decide everything. 'the website' (+0.203), 'website' (+0.196), 'following recent' (+0.173) and 'marketing' (+0.135) push to IT Support. The gap is large (0.222).

#### Ticket 1134
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: The problem is data integration between an Oracle database and marketing tools. The word 'marketing' pushes to IT Support even though it says nothing about the fault.
- Why the model chose IT Support: 'marketing' (+0.102), 'marketing tools' (+0.101), 'database and' (+0.085) and 'tools' (+0.084) push to IT Support (gap 0.123). The Technical Support words are weaker: 'campaigns' (-0.122) and 'data' (-0.082). Technical Support is only third; Product Support is second.

#### Ticket 1158
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: The ticket says 'digital tools' are not working. It names no product and no error. The generic words 'tools' and 'devices' decide the result.
- Why the model chose IT Support: The gap is small (0.044). 'digital tools' (+0.128), 'tools' (+0.100), 'or hardware' (+0.097) and 'devices' (+0.070) push to IT Support. 'agency are' (-0.090) pushes the other way.

#### Ticket 1227
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: PowerPoint, JIRA and Figma are not working, but the ticket describes it with generic words like 'problems' and 'digital tools'.
- Why the model chose IT Support: It is almost a tie (gap 0.015). 'problems' (+0.110), 'the problems' (+0.101) and 'digital tools' (+0.101) push to IT Support. 'incompatibility' (-0.123) and 'jira' (-0.076) push to Technical Support and almost win.

#### Ticket 1339
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: Scanners, antivirus and peripherals fail because of a hardware and software conflict. The words are about hardware and devices.
- Why the model chose IT Support: The model is confident (gap 0.172). 'and software' (+0.213), 'malfunctions' (+0.168) and 'the problems' (+0.137) push to IT Support. Only 58 words are known, and 'device' (-0.091) is the main push back.

#### Ticket 1355
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Label could be IT Support
- Why this category: Someone tried to get into hospital systems without permission. The customer updated firewall rules and login alerts. Security and access fit IT Support.
- Why the model chose IT Support: 'updated the' (+0.086), 'cause and' (+0.084), 'access' (+0.083) and 'been detected' (+0.064) push to IT Support (gap 0.121). 'firewall' (-0.070) and 'patches' (-0.064) push to Technical Support but are weak.

#### Ticket 1448
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: The analytics platform has connection problems and the servers were restarted. The words are about connectivity and servers.
- Why the model chose IT Support: 'connectivity problems' (+0.235), 'connectivity' (+0.136) and 'the servers' (+0.134) push to IT Support (gap 0.153). 'platform' (-0.132) and 'analytics' (-0.098) push to Technical Support. The ticket is short (206 characters).

#### Ticket 1465
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: A software bug or setting error in an analytics system, with common troubleshooting steps. It looks like a Technical Support fault, but generic software words push the model to IT Support.
- Why the model chose IT Support: 'bug' (+0.123), 'software to' (+0.112) and 'software bug' (+0.082) push to IT Support (gap 0.129). Technical Support is only third, behind Human Resources, so the ticket gives it little support.

#### Ticket 1774
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: A project management platform is slow because of server overload. The servers were restarted. The words are about servers and slowness.
- Why the model chose IT Support: The gap is small (0.025). 'server' (+0.097), 'sluggish' (+0.079) and 'servers and' (+0.072) push to IT Support. 'the project' (-0.077) and 'platform' (-0.070) push to Technical Support.

#### Ticket 1865
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: Marketing systems are disrupted by a software or hardware conflict. No product is named. The word 'marketing' and generic phrases decide the result.
- Why the model chose IT Support: It is almost a tie (gap 0.020). 'marketing' (+0.103), 'or hardware' (+0.082) and 'concerns about' (+0.062) push to IT Support. 'to software' (-0.115) and 'digital strategies' (-0.095) push to Technical Support.

#### Ticket 2024
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Very short ticket
- Why this category: The ticket is one sentence: 54 characters and 13 known words ('Encountering sporadic failures with the digital tools.'). It has no detail.
- Why the model chose IT Support: 'digital tools' (+0.341) and 'tools' (+0.265) decide the result (gap 0.140). Product Support is second (0.220), so the model is not sure.

#### Ticket 2030
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: A hospital cannot access data in its systems after software updates. The ticket has no technical detail, and the biggest push comes from a common word.
- Why the model chose IT Support: It is almost a tie (gap 0.013). The biggest pushes to IT Support are common words: 'to' (+0.112), 'rebooting the' (+0.089) and 'disruptions' (+0.081). 'to resolve' (-0.116) pushes to Technical Support.

#### Ticket 2161
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: A campaign platform crashed after a software update. This is a Technical Support fault, but common words like 'current' and 'it' push to IT Support.
- Why the model chose IT Support: 'current' (+0.122, from 'current campaigns'), 'suspected that' (+0.090) and 'it' (+0.070) push to IT Support (gap 0.066). 'platform' (-0.138) and 'campaign' (-0.107) push to Technical Support.

#### Ticket 2355
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: An incident hits Microsoft Office, PostgreSQL, Git and Oracle Database, blamed on server overload. The word 'server' dominates, and the products are not told apart.
- Why the model chose IT Support: 'server' (+0.096), 'updates the' (+0.076) and 'office' (+0.056) push to IT Support (gap 0.065). 'postgresql' (-0.127), 'issue appears' (-0.067) and 'git' (-0.056) push to Technical Support.

#### Ticket 2411
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Very short ticket
- Why this category: The ticket is one sentence: 61 characters and 13 known words ('Detected unauthorized attempts to access medical information.'). The topic also fits IT Support.
- Why the model chose IT Support: 'detected' (+0.164), 'access' (+0.142) and 'detected unauthorized' (+0.103) push to IT Support (gap 0.054). Product Support is second (0.180), so the model is not sure.

#### Ticket 2613
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Label could be IT Support
- Why this category: The customer asks for a plan to update and improve integrations. No fault is reported. A request for advice fits IT Support.
- Why the model chose IT Support: The gap is small (0.043). 'enhance' (+0.090), 'slowdowns' (+0.089) and 'request' (+0.075) push to IT Support. 'integrations' (-0.108) pushes to Technical Support. Customer Service is second (0.183).

#### Ticket 2620
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Label could be IT Support
- Why this category: The customer cannot log in and already reset passwords. Login and password problems are normal IT Support tickets.
- Why the model chose IT Support: The gap is small (0.044). 'resetting passwords' (+0.098), 'problems that' (+0.079) and 'problems' (+0.071) push to IT Support. 'advise on' (-0.082) and 'recent update' (-0.067) push to Technical Support. Product Support is second (0.204).

#### Ticket 2818
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: A marketing agency's website goes down, blamed on server overload. The server was restarted. The words are about the server and the website.
- Why the model chose IT Support: The gap is small (0.031). 'server' (+0.170), 'website' (+0.066) and 'agency website' (+0.063) push to IT Support. 'in investigating' (-0.092) and 'problem with' (-0.080) push to Technical Support.

#### Ticket 2890
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: Software and hardware parts fail in a project management tool after an update. The ticket uses generic words ('malfunctions', 'problems', 'tools') and names no error.
- Why the model chose IT Support: 'malfunctions' (+0.118), 'software the' (+0.105), 'the problems' (+0.097) and 'tools' (+0.075) push to IT Support (gap 0.067). 'project' (-0.099) and 'report regarding' (-0.079) push to Technical Support.

#### Ticket 3049
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Label could be IT Support
- Why this category: The customer asks to change how data analytics tools are integrated to improve investment strategy. No fault is reported, so the ticket could fit several departments.
- Why the model chose IT Support: The model is unsure: IT Support 0.194, Customer Service 0.193, General Inquiry 0.183. 'tools' (+0.214), 'to make' (+0.106) and 'current' (+0.104) push to IT Support. 'data' (-0.140) and 'analytics' (-0.130) push to Technical Support.

#### Ticket 3450
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: A marketing agency's website loads slowly after plugin updates. The cache was cleared and the server restarted. The words are about the server and loading.
- Why the model chose IT Support: 'loading times' (+0.139), 'server' (+0.121) and 'sluggish' (+0.099) push to IT Support (gap 0.137). 'and the' (-0.088) and 'is experiencing' (-0.080) push to Technical Support. The ticket is short (210 characters).

#### Ticket 3625
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: Marketing tools (Adobe Sign, PrestaShop, Elasticsearch) stopped working after updates and network problems. The generic word 'tools' decides the result. This ticket is almost the same as 4029.
- Why the model chose IT Support: It is almost a tie (gap 0.032). 'tools' (+0.160), 'access and' (+0.109) and 'marketing tools' (+0.096) push to IT Support. 'campaign' (-0.102) and 'elasticsearch' (-0.084) push to Technical Support.

#### Ticket 3915
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: An analytics system fails on and off, from software incompatibility or hardware. The ticket uses generic phrases like 'software the' and 'request'.
- Why the model chose IT Support: 'software the' (+0.136), 'request' (+0.096) and 'or hardware' (+0.095) push to IT Support (gap 0.062). 'incompatibility' (-0.153) is in the ticket and pushes to Technical Support, but it is not enough.

#### Ticket 3936
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: System performance drops across devices and software after updates. The ticket uses generic words and names no product.
- Why the model chose IT Support: 'software the' (+0.117), 'multiple devices' (+0.103) and 'and software' (+0.084) push to IT Support (gap 0.058). 'despite these' (-0.068) and 'report' (-0.067) push to Technical Support but are weak.

#### Ticket 3949
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Label could be IT Support
- Why this category: The customer asks for best practices to protect medical data. No fault is reported. Security advice fits IT Support.
- Why the model chose IT Support: The model is unsure: IT Support 0.176, Product Support 0.140, Technical Support 0.124. 'devices' (+0.119), 'and integrity' (+0.110) and 'offer guidance' (+0.107) push to IT Support. 'for securing' (-0.103) and 'data' (-0.083) push to Technical Support.

#### Ticket 4029
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Generic words
- Why this category: Marketing tools (Adobe Sign, PrestaShop, Elasticsearch) stopped working after updates and network problems. The generic word 'tools' decides the result. This ticket is almost the same as 3625.
- Why the model chose IT Support: It is almost a tie (gap 0.015). 'tools' (+0.161), 'access and' (+0.110) and 'marketing tools' (+0.097) push to IT Support. 'campaign' (-0.103) and 'elasticsearch' (-0.085) push to Technical Support.

#### Ticket 4255
- True label: Technical Support
- Predicted label (recommended_department): IT Support
- Category: Network and server words
- Why this category: Marketing campaigns stop because of connection problems and a modem failure tied to Firebase. The words are about the network, the connection and a product name the model links to IT.
- Why the model chose IT Support: The model is confident (gap 0.172). 'firebase' (+0.170), 'marketing' (+0.103), 'network' (+0.097) and 'connectivity' (+0.071) push to IT Support. 'these' (-0.109) and 'campaigns' (-0.061) push to Technical Support.

### Failure categories

#### Generic words
- Definition: The push to IT Support comes from common words like 'tools', 'problems', 'current', 'it' or 'marketing'. Nothing technical in the ticket separates the two departments.
- Count: 12 of 30
- Impact: 12 of 30 inspected errors (40%). 6 are near ties (gap under 0.05), so small changes can flip them. Estimate for the whole slice: about 64 of the 159 tickets (3.2% of all 1982 validation errors). It comes from the first 30 tickets, so it is only an estimate.
- Can a model or preprocessing change fix it? Yes. Common words carry a push to IT Support. Removing very common words (stop words or a lower max_df) or using stronger regularization reduces it. Risk: lowercasing makes the pronoun 'it' look like the acronym 'IT', so removing 'it' can remove a real IT Support signal.

#### Network and server words
- Definition: The words that push the model to IT Support are network, server, connection or hardware words. The ticket is really about a product, an app or a device fault.
- Count: 10 of 30
- Impact: 10 of 30 inspected errors. 3 are confident errors (gap above 0.15). Estimate for the whole slice: about 53 of the 159 tickets (2.7% of all 1982 validation errors). It comes from the first 30 tickets, so it is only an estimate.
- Can a model or preprocessing change fix it? Partly. Stronger regularization or different word weighting could reduce how much one word like 'network' decides. The risk is high. These words are real IT Support signals, and 107 IT Support tickets already go to Technical Support. I did not test this on real IT Support tickets.

#### Label could be IT Support
- Definition: The ticket is about access, security or a request for advice, not a fault. IT Support is a reasonable department, so the true label is debatable.
- Count: 5 of 30
- Impact: 5 of 30 inspected errors (17%). Some of these may be label problems, not model errors. Estimate for the whole slice: about 26 of the 159 tickets (1.3% of all 1982 validation errors). It comes from the first 30 tickets, so it is only an estimate.
- Can a model or preprocessing change fix it? No. The text supports the model's choice. Forcing these back to Technical Support would fit unclear labels and could hurt IT Support recall.

#### Very short ticket
- Definition: The ticket is one short sentence (about 100 characters or less, 21 or fewer words the model knows). A few words decide the result.
- Count: 3 of 30
- Impact: 3 of 30 inspected errors (10%). 2 are confident errors from very few words. Estimate for the whole slice: about 16 of the 159 tickets (0.8% of all 1982 validation errors). It comes from the first 30 tickets, so it is only an estimate.
- Can a model or preprocessing change fix it? No. The ticket has too little text. No model setting adds information. It needs a longer description or a human check.

The counts add up to 30 tickets.

### Task 2 candidate
- Category to target: Generic words
- Change to try: Remove very common words from the text features (stop words or a lower max_df) and retrain on the training split.
- Expected gain: Some of the 12 tickets, mainly the 6 near ties, should move to Technical Support.
- Risk: IT Support could lose recall if 'it' or other useful common words are removed. Check the 107 IT Support tickets already sent to Technical Support.
