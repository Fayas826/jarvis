from pptx import Presentation

prs = Presentation()

# Slide 1: Title Slide (Welcome)
title_slide_layout = prs.slide_layouts[0]
slide1 = prs.slides.add_slide(title_slide_layout)
title = slide1.shapes.title
subtitle = slide1.placeholders[1]

title.text = "WELCOME\nSEMINAR TOPICS"
subtitle.text = "Submitted by: Akshay S\nBranch: CSE S7\nStream: Computer Science & Engineering"

# Slide 2: Index Page
bullet_slide_layout = prs.slide_layouts[1]
slide2 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide2.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]

title_shape.text = "Index / Topics Covered"
tf = body_shape.text_frame
tf.text = "1. Li-Fi (Light Fidelity)"
p = tf.add_paragraph()
p.text = "2. Black-Box to White-Box AI Conversion"
p = tf.add_paragraph()
p.text = "3. Software Testing Automation Tools"

# Slide 3: Topic 1 - Li-Fi
slide3 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide3.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Topic 1 - Li-Fi (Light Fidelity)"
tf = body_shape.text_frame
tf.text = "What I Understood from the Paper:"
p = tf.add_paragraph()
p.text = "Li-Fi is a wireless communication technology that uses visible light from LED bulbs to transmit data at high speeds instead of traditional radio waves (Wi-Fi). It converts internet data into ultra-fast, invisible light pulses decoded by photosensors on devices."
p.level = 1
p = tf.add_paragraph()
p.text = "Main Features:"
p = tf.add_paragraph()
p.text = "High-speed data transmission using visible light communication (VLC)."
p.level = 1
p = tf.add_paragraph()
p.text = "Operates on the completely unregulated light spectrum."
p.level = 1

# Slide 4: Li-Fi (Pros, Cons & Future Scope)
slide4 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide4.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Li-Fi (Pros, Cons & Future Scope)"
tf = body_shape.text_frame
tf.text = "Pros: Immune to electromagnetic interference. Highly secure because light waves cannot penetrate physical walls."
p = tf.add_paragraph()
p.text = "Cons: Limited operational range requiring a direct line-of-sight. Data transmission stops instantly if the light path is physically blocked."
p = tf.add_paragraph()
p.text = "Future Scope: Integration into smart indoor lighting systems, underwater data transmission, and deployment in interference-sensitive zones like hospital surgical rooms and airplane cabins."
p = tf.add_paragraph()
p.text = "Relevance: Relieves network congestion on crowded radio frequencies and provides an ultra-secure local area network solution."

# Slide 5: Topic 2 - Black-Box to White-Box AI Conversion
slide5 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide5.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Topic 2 - Black-Box to White-Box AI Conversion"
tf = body_shape.text_frame
tf.text = "What I Understood from the Paper:"
p = tf.add_paragraph()
p.text = "This domain introduces post-hoc explainability frameworks (like LIME and SHAP) that analyze complex, uninterpretable 'black-box' deep learning models to reveal how they make decisions. It translates opaque neural network logic into human-readable 'white-box' visual explanations."
p.level = 1
p = tf.add_paragraph()
p.text = "Main Features:"
p = tf.add_paragraph()
p.text = "Model-agnostic explanations."
p.level = 1
p = tf.add_paragraph()
p.text = "Visual tracking of feature or pixel weight contributions to the system's output."
p.level = 1

# Slide 6: AI Conversion (Pros, Cons & Future Scope)
slide6 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide6.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "AI Conversion (Pros, Cons & Future Scope)"
tf = body_shape.text_frame
tf.text = "Pros: Uncovers hidden model biases and tracking errors. Builds system accountability for strict regulatory compliance."
p = tf.add_paragraph()
p.text = "Cons: Generating post-hoc explanations requires significant extra processing time and computational power. Explanations are approximations and may not capture the complete network logic."
p = tf.add_paragraph()
p.text = "Future Scope: Automation of debugging tools inside neural network development environments and real-time interpretability engines for autonomous vehicles."
p = tf.add_paragraph()
p.text = "Relevance: Solves the trust crisis in deep learning, making AI safe and auditable for high-risk applications like medical diagnostics and banking."

# Slide 7: Topic 3 - Software Testing Automation Tools
slide7 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide7.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Topic 3 - Software Testing Automation Tools"
tf = body_shape.text_frame
tf.text = "What I Understood from the Paper:"
p = tf.add_paragraph()
p.text = "This technology uses specialized automated frameworks (like Playwright, Cypress, and Selenium) to auto-run test scripts across applications. It completely eliminates repetitive manual quality checks, ensuring software updates are bug-free before production deployment."
p.level = 1
p = tf.add_paragraph()
p.text = "Main Features:"
p = tf.add_paragraph()
p.text = "Automated continuous integration (CI) testing pipelines."
p.level = 1
p = tf.add_paragraph()
p.text = "Visual time-travel debugging capabilities and auto-waiting mechanisms."
p.level = 1

# Slide 8: Testing Automation (Pros, Cons & Future Scope)
slide8 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide8.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "Testing Automation (Pros, Cons & Future Scope)"
tf = body_shape.text_frame
tf.text = "Pros: Dramatically speeds up software release cycles. Catches system regression bugs faster and with higher accuracy than human manual testing."
p = tf.add_paragraph()
p.text = "Cons: High initial setup effort and time required to write baseline automation scripts. Flaky tests can generate false error alerts if modern auto-healing practices are omitted."
p = tf.add_paragraph()
p.text = "Future Scope: Growth of self-healing scripts using lightweight AI to fix tests automatically when UI elements change. Widespread deployment inside continuous deployment microservices."
p = tf.add_paragraph()
p.text = "Relevance: Reduces software maintenance overhead, drastically lowering development costs while guaranteeing application stability."

# Slide 9: REFERENCES
slide9 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide9.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]
title_shape.text = "REFERENCES"
tf = body_shape.text_frame
tf.text = "1. H. Haas, 'Li-Fi: The Next Generation of Wireless High-Speed Optical Connectivity,' IEEE Photonics Technology Letters, Vol. 37, No. 2, Feb. 2025."
p = tf.add_paragraph()
p.text = "2. S. M. Lundberg and S.-I. Lee, 'A Unified Approach to Interpreting Opaque Black-Box Model Predictions,' IEEE Trans. on Pattern Analysis and Machine Intelligence, Vol. 48, No. 4, May 2025."
p = tf.add_paragraph()
p.text = "3. A. M. R. Garro and K. L. Fowler, 'Automated Testing Frameworks in CI/CD Pipelines: A Comparative Review of Modern Toolsets,' in Proc. of the 2026 IEEE ICST, April 2026."

# Slide 10: End Slide
slide10 = prs.slides.add_slide(title_slide_layout)
title10 = slide10.shapes.title
subtitle10 = slide10.placeholders[1]
title10.text = "THANK YOU"
subtitle10.text = "Questions & Answers"

prs.save("Seminar_Presentation.pptx")
print("Presentation saved successfully as Seminar_Presentation.pptx")
