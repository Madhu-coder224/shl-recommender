import os
import json
import logging
from typing import Literal, List, Optional

import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SHL Assessment Recommender", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG_TEXT = """- .NET Framework 4.5 | https://www.shl.com/products/product-catalog/view/net-framework-4-5/ | Knowledge & Skills
- .NET MVC (New) | https://www.shl.com/products/product-catalog/view/net-mvc-new/ | Knowledge & Skills
- .NET MVVM (New) | https://www.shl.com/products/product-catalog/view/net-mvvm-new/ | Knowledge & Skills
- .NET WCF (New) | https://www.shl.com/products/product-catalog/view/net-wcf-new/ | Knowledge & Skills
- .NET WPF (New) | https://www.shl.com/products/product-catalog/view/net-wpf-new/ | Knowledge & Skills
- .NET XAML (New) | https://www.shl.com/products/product-catalog/view/net-xaml-new/ | Knowledge & Skills
- 360 Digital Report | https://www.shl.com/products/product-catalog/view/360-digital-report/ | Development & 360
- 360° Multi-Rater Feedback System (MFS) | https://www.shl.com/products/product-catalog/view/360-multi-rater-feedback-system-mfs/ | Development & 360, Personality & Behavior
- ADO.NET (New) | https://www.shl.com/products/product-catalog/view/ado-net-new/ | Knowledge & Skills
- AI Skills | https://www.shl.com/products/product-catalog/view/ai-skills/ | Personality & Behavior
- ASP .NET with C# (New) | https://www.shl.com/products/product-catalog/view/asp-net-with-c-new/ | Knowledge & Skills
- ASP.NET 4.5 | https://www.shl.com/products/product-catalog/view/asp-net-4-5/ | Knowledge & Skills
- Accounts Payable (New) | https://www.shl.com/products/product-catalog/view/accounts-payable-new/ | Knowledge & Skills
- Accounts Payable Simulation (New) | https://www.shl.com/products/product-catalog/view/accounts-payable-simulation-new/ | Simulations
- Accounts Receivable (New) | https://www.shl.com/products/product-catalog/view/accounts-receivable-new/ | Knowledge & Skills
- Accounts Receivable Simulation (New) | https://www.shl.com/products/product-catalog/view/accounts-receivable-simulation-new/ | Simulations
- Adobe Experience Manager (New) | https://www.shl.com/products/product-catalog/view/adobe-experience-manager-new/ | Knowledge & Skills
- Adobe Photoshop CC | https://www.shl.com/products/product-catalog/view/adobe-photoshop-cc/ | Knowledge & Skills
- Aeronautical Engineering (New) | https://www.shl.com/products/product-catalog/view/aeronautical-engineering-new/ | Knowledge & Skills
- Aerospace Engineering (New) | https://www.shl.com/products/product-catalog/view/aerospace-engineering-new/ | Knowledge & Skills
- Agile Software Development | https://www.shl.com/products/product-catalog/view/agile-software-development/ | Knowledge & Skills
- Agile Testing (New) | https://www.shl.com/products/product-catalog/view/agile-testing-new/ | Knowledge & Skills
- Amazon Web Services (AWS) Development (New) | https://www.shl.com/products/product-catalog/view/amazon-web-services-aws-development-new/ | Knowledge & Skills
- Android Development (New) | https://www.shl.com/products/product-catalog/view/android-development-new/ | Knowledge & Skills
- Angular 6 (New) | https://www.shl.com/products/product-catalog/view/angular-6-new/ | Knowledge & Skills
- AngularJS (New) | https://www.shl.com/products/product-catalog/view/angularjs-new/ | Knowledge & Skills
- Apache HBase (New) | https://www.shl.com/products/product-catalog/view/apache-hbase-new/ | Knowledge & Skills
- Apache Hadoop (New) | https://www.shl.com/products/product-catalog/view/apache-hadoop-new/ | Knowledge & Skills
- Apache Hadoop Extensions (New) | https://www.shl.com/products/product-catalog/view/apache-hadoop-extensions-new/ | Knowledge & Skills
- Apache Hive (New) | https://www.shl.com/products/product-catalog/view/apache-hive-new/ | Knowledge & Skills
- Apache Kafka (New) | https://www.shl.com/products/product-catalog/view/apache-kafka-new/ | Knowledge & Skills
- Apache Pig (New) | https://www.shl.com/products/product-catalog/view/apache-pig-new/ | Knowledge & Skills
- Apache Spark (New) | https://www.shl.com/products/product-catalog/view/apache-spark-new/ | Knowledge & Skills
- Assessment and Development Center Exercises | https://www.shl.com/products/product-catalog/view/assessment-and-development-center-exercises/ | Assessment Exercises
- Automata (New) | https://www.shl.com/products/product-catalog/view/automata-new/ | Simulations
- Automata - Fix (New) | https://www.shl.com/products/product-catalog/view/automata-fix-new/ | Simulations
- Automata - SQL (New) | https://www.shl.com/products/product-catalog/view/automata-sql-new/ | Simulations
- Automata Data Science (New) | https://www.shl.com/products/product-catalog/view/automata-data-science-new/ | Simulations
- Automata Data Science Pro (New) | https://www.shl.com/products/product-catalog/view/automata-data-science-pro-new/ | Simulations
- Automata Front End | https://www.shl.com/products/product-catalog/view/automata-front-end/ | Simulations
- Automata Pro (New) | https://www.shl.com/products/product-catalog/view/automata-pro-new/ | Simulations
- Automata Selenium | https://www.shl.com/products/product-catalog/view/automata-selenium/ | Simulations
- Automation Anywhere RPA Development (New) | https://www.shl.com/products/product-catalog/view/automation-anywhere-rpa-development-new/ | Knowledge & Skills
- Automotive Engineering (New) | https://www.shl.com/products/product-catalog/view/automotive-engineering-new/ | Knowledge & Skills
- Basic Biology (New) | https://www.shl.com/products/product-catalog/view/basic-biology-new/ | Knowledge & Skills
- Basic Computer Literacy (Windows 10) (New) | https://www.shl.com/products/product-catalog/view/basic-computer-literacy-windows-10-new/ | Simulations, Knowledge & Skills
- Basic Statistics (New) | https://www.shl.com/products/product-catalog/view/basic-statistics-new/ | Knowledge & Skills
- Biochemistry (New) | https://www.shl.com/products/product-catalog/view/biochemistry-new/ | Knowledge & Skills
- Biotech Lab Techniques (New) | https://www.shl.com/products/product-catalog/view/biotech-lab-techniques-new/ | Knowledge & Skills
- BizTalk (New) | https://www.shl.com/products/product-catalog/view/biztalk-new/ | Knowledge & Skills
- Business Communication (adaptive) | https://www.shl.com/products/product-catalog/view/business-communication-adaptive/ | Knowledge & Skills
- Business Communications | https://www.shl.com/products/product-catalog/view/business-communications/ | Knowledge & Skills
- C Programming (New) | https://www.shl.com/products/product-catalog/view/c-programming-new/ | Knowledge & Skills
- C# Programming (New) | https://www.shl.com/products/product-catalog/view/c-programming-new-4039/ | Knowledge & Skills
- C++ Programming (New) | https://www.shl.com/products/product-catalog/view/c-programming-new-4122/ | Knowledge & Skills
- COBOL Programming (New) | https://www.shl.com/products/product-catalog/view/cobol-programming-new/ | Knowledge & Skills
- CSS3 (New) | https://www.shl.com/products/product-catalog/view/css3-new/ | Knowledge & Skills
- Cardiology and Diabetes Management (New) | https://www.shl.com/products/product-catalog/view/cardiology-and-diabetes-management-new/ | Knowledge & Skills
- Ceramic Engineering (New) | https://www.shl.com/products/product-catalog/view/ceramic-engineering-new/ | Knowledge & Skills
- Chemical Engineering (New) | https://www.shl.com/products/product-catalog/view/chemical-engineering-new/ | Knowledge & Skills
- Cisco AppDynamics (New) | https://www.shl.com/products/product-catalog/view/cisco-appdynamics-new/ | Knowledge & Skills
- Civil Engineering (New) | https://www.shl.com/products/product-catalog/view/civil-engineering-new/ | Knowledge & Skills
- Cloud Computing (New) | https://www.shl.com/products/product-catalog/view/cloud-computing-new/ | Knowledge & Skills
- Computer Science (New) | https://www.shl.com/products/product-catalog/view/computer-science-new/ | Knowledge & Skills
- Contact Center Call Simulation (New) | https://www.shl.com/products/product-catalog/view/contact-center-call-simulation-new/ | Simulations
- Conversational Multichat Simulation | https://www.shl.com/products/product-catalog/view/conversational-multichat-simulation/ | Simulations
- Core Java (Advanced Level) (New) | https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/ | Knowledge & Skills
- Core Java (Entry Level) (New) | https://www.shl.com/products/product-catalog/view/core-java-entry-level-new/ | Knowledge & Skills
- Count Out The Money | https://www.shl.com/products/product-catalog/view/count-out-the-money/ | Knowledge & Skills, Simulations
- Culinary Skills (New) | https://www.shl.com/products/product-catalog/view/culinary-skills-new/ | Knowledge & Skills
- Customer Service Phone Simulation | https://www.shl.com/products/product-catalog/view/customer-service-phone-simulation/ | Biodata & Situational Judgement, Simulations
- Customer Service Phone Solution | https://www.shl.com/products/product-catalog/view/customer-service-phone-solution/ | Biodata & Situational Judgement, Personality & Behavior, Simulations
- Cyber Risk (New) | https://www.shl.com/products/product-catalog/view/cyber-risk-new/ | Knowledge & Skills
- DSI v1.1 Interpretation Report | https://www.shl.com/products/product-catalog/view/dsi-v1-1-interpretation-report/ | Personality & Behavior
- Data Entry (New) | https://www.shl.com/products/product-catalog/view/data-entry-new/ | Simulations
- Data Entry Alphanumeric Split Screen - US | https://www.shl.com/products/product-catalog/view/data-entry-alphanumeric-split-screen-us/ | Knowledge & Skills
- Data Entry Numeric Split Screen - US | https://www.shl.com/products/product-catalog/view/data-entry-numeric-split-screen-us/ | Knowledge & Skills
- Data Entry Ten Key Split Screen | https://www.shl.com/products/product-catalog/view/data-entry-ten-key-split-screen/ | Knowledge & Skills
- Data Science (New) | https://www.shl.com/products/product-catalog/view/data-science-new/ | Knowledge & Skills
- Data Warehousing Concepts | https://www.shl.com/products/product-catalog/view/data-warehousing-concepts/ | Knowledge & Skills
- Dependability and Safety Instrument (DSI) | https://www.shl.com/products/product-catalog/view/dependability-and-safety-instrument-dsi/ | Personality & Behavior
- Dermatology (New) | https://www.shl.com/products/product-catalog/view/dermatology-new/ | Knowledge & Skills
- Desktop Support (New) | https://www.shl.com/products/product-catalog/view/desktop-support-new/ | Knowledge & Skills
- Digital Advertising (New) | https://www.shl.com/products/product-catalog/view/digital-advertising-new/ | Knowledge & Skills
- Digital Readiness Development Report - IC | https://www.shl.com/products/product-catalog/view/digital-readiness-development-report/ | Personality & Behavior
- Digital Readiness Development Report - Manager | https://www.shl.com/products/product-catalog/view/digital-readiness-development-report-manager/ | Personality & Behavior
- Docker (New) | https://www.shl.com/products/product-catalog/view/docker-new/ | Knowledge & Skills
- Dojo (New) | https://www.shl.com/products/product-catalog/view/dojo-new/ | Knowledge & Skills
- Drupal (New) | https://www.shl.com/products/product-catalog/view/drupal-new/ | Knowledge & Skills
- ETL Testing (New) | https://www.shl.com/products/product-catalog/view/etl-testing-new/ | Knowledge & Skills
- Econometrics (New) | https://www.shl.com/products/product-catalog/view/econometrics-new/ | Knowledge & Skills
- Economics (New) | https://www.shl.com/products/product-catalog/view/economics-new/ | Knowledge & Skills
- Electrical Engineering (New) | https://www.shl.com/products/product-catalog/view/electrical-engineering-new/ | Knowledge & Skills
- Electrical and Electronics Engineering (New) | https://www.shl.com/products/product-catalog/view/electrical-and-electronics-engineering-new/ | Knowledge & Skills
- Electronics & Telecommunications Engineering (New) | https://www.shl.com/products/product-catalog/view/electronics-and-telecommunications-engineering-new/ | Knowledge & Skills
- Electronics and Embedded Systems Engineering (New) | https://www.shl.com/products/product-catalog/view/electronics-and-embedded-systems-engineering-new/ | Knowledge & Skills
- Electronics and Semiconductor Engineering (New) | https://www.shl.com/products/product-catalog/view/electronics-and-semiconductor-engineering-new/ | Knowledge & Skills
- English Comprehension (New) | https://www.shl.com/products/product-catalog/view/english-comprehension-new/ | Knowledge & Skills
- Enterprise Java Beans (New) | https://www.shl.com/products/product-catalog/view/enterprise-java-beans-new/ | Knowledge & Skills
- Enterprise Leadership Report 1.0 | https://www.shl.com/products/product-catalog/view/enterprise-leadership-report/ | Personality & Behavior
- Enterprise Leadership Report 2.0 | https://www.shl.com/products/product-catalog/view/enterprise-leadership-report-2-0/ | Personality & Behavior
- Entry Level Cashier Solution | https://www.shl.com/products/product-catalog/view/entry-level-cashier-solution/ | Competencies, Personality & Behavior
- Entry Level Customer Serv-Retail & Contact Center | https://www.shl.com/products/product-catalog/view/entry-level-customer-serv-retail-and-contact-center/ | Personality & Behavior, Competencies
- Entry Level Customer Service (General) Solution | https://www.shl.com/products/product-catalog/view/entry-level-customer-service-general-solution/ | Competencies, Personality & Behavior
- Entry Level Hotel Front Desk Solution | https://www.shl.com/products/product-catalog/view/entry-level-hotel-front-desk-solution/ | Competencies, Personality & Behavior
- Entry Level Sales Solution | https://www.shl.com/products/product-catalog/view/entry-level-sales-solution/ | Competencies, Personality & Behavior
- Entry Level Technical Support Solution | https://www.shl.com/products/product-catalog/view/entry-level-technical-support-solution/ | Personality & Behavior, Competencies
- Executive Scenarios | https://www.shl.com/products/product-catalog/view/executive-scenarios/ | Biodata & Situational Judgement
- Executive Scenarios Narrative Report | https://www.shl.com/products/product-catalog/view/executive-scenarios-narrative-report/ | Biodata & Situational Judgement
- Executive Scenarios Profile Report | https://www.shl.com/products/product-catalog/view/executive-scenarios-profile-report/ | Biodata & Situational Judgement
- ExpressJS (New) | https://www.shl.com/products/product-catalog/view/expressjs-new/ | Knowledge & Skills
- Filing - Names (R1) | https://www.shl.com/products/product-catalog/view/filing-names-r1/ | Knowledge & Skills
- Filing - Numbers | https://www.shl.com/products/product-catalog/view/filing-numbers/ | Knowledge & Skills
- Financial Accounting (New) | https://www.shl.com/products/product-catalog/view/financial-accounting-new/ | Knowledge & Skills
- Financial and Banking Services (New) | https://www.shl.com/products/product-catalog/view/financial-and-banking-services-new/ | Knowledge & Skills
- Fire Engineering (New) | https://www.shl.com/products/product-catalog/view/fire-engineering-new/ | Knowledge & Skills
- Following Instructions v1 - UK (R1) | https://www.shl.com/products/product-catalog/view/following-instructions-v1-uk-r1/ | Knowledge & Skills
- Following Instructions v1 - US (R2) | https://www.shl.com/products/product-catalog/view/following-instructions-v1-us-r2/ | Knowledge & Skills
- Food Science (New) | https://www.shl.com/products/product-catalog/view/food-science-new/ | Knowledge & Skills
- Food and Beverage Services (New) | https://www.shl.com/products/product-catalog/view/food-and-beverage-services-new/ | Knowledge & Skills
- Front Office Management (New) | https://www.shl.com/products/product-catalog/view/front-office-management-new/ | Knowledge & Skills
- Fundamentals of Chemistry (New) | https://www.shl.com/products/product-catalog/view/fundamentals-of-chemistry-new/ | Knowledge & Skills
- Fundamentals of Physics (New) | https://www.shl.com/products/product-catalog/view/fundamentals-of-physics-new/ | Knowledge & Skills
- GIT (New) | https://www.shl.com/products/product-catalog/view/git-new/ | Knowledge & Skills
- General Diseases (New) | https://www.shl.com/products/product-catalog/view/general-diseases-new/ | Knowledge & Skills
- Geoinformatics Engineering (New) | https://www.shl.com/products/product-catalog/view/geoinformatics-engineering-new/ | Knowledge & Skills
- Geoscience Engineering (New) | https://www.shl.com/products/product-catalog/view/geoscience-engineering-new/ | Knowledge & Skills
- Global Skills Assessment | https://www.shl.com/products/product-catalog/view/global-skills-assessment/ | Competencies, Knowledge & Skills
- Global Skills Development Report | https://www.shl.com/products/product-catalog/view/global-skills-development-report/ | Ability & Aptitude, Assessment Exercises, Biodata & Situational Judgement, Competencies, Development & 360, Personality & Behavior
- Graduate Scenarios | https://www.shl.com/products/product-catalog/view/graduate-scenarios/ | Biodata & Situational Judgement
- Graduate Scenarios Narrative Report | https://www.shl.com/products/product-catalog/view/graduate-scenarios-narrative-report/ | Biodata & Situational Judgement
- Graduate Scenarios Profile Report | https://www.shl.com/products/product-catalog/view/graduate-scenarios-profile-report/ | Biodata & Situational Judgement
- HIPAA (Security) | https://www.shl.com/products/product-catalog/view/hipaa-security/ | Knowledge & Skills
- HTML/CSS (New) | https://www.shl.com/products/product-catalog/view/htmlcss-new/ | Knowledge & Skills
- HTML5 (New) | https://www.shl.com/products/product-catalog/view/html5-new/ | Knowledge & Skills
- HiPo Assessment Report 1.0 | https://www.shl.com/products/product-catalog/view/hipo-assessment-report-1-0/ | Competencies, Personality & Behavior
- HiPo Assessment Report 2.0 | https://www.shl.com/products/product-catalog/view/hipo-assessment-report-2-0/ | Competencies, Personality & Behavior
- HiPo Unlocking Potential Report 2.0 | https://www.shl.com/products/product-catalog/view/hipo-unlocking-potential-report-2-0/ | Competencies
- Hibernate (New) | https://www.shl.com/products/product-catalog/view/hibernate-new/ | Knowledge & Skills
- Housekeeping (New) | https://www.shl.com/products/product-catalog/view/housekeeping-new/ | Knowledge & Skills
- Human Resources (New) | https://www.shl.com/products/product-catalog/view/human-resources-new/ | Knowledge & Skills
- IBM DataStage (New) | https://www.shl.com/products/product-catalog/view/ibm-datastage-new/ | Knowledge & Skills
- IBM Sterling Order Management System (New) | https://www.shl.com/products/product-catalog/view/ibm-sterling-order-management-system-new/ | Knowledge & Skills
- ITIL (IT Infrastructure Library) (New) | https://www.shl.com/products/product-catalog/view/itil-it-infrastructure-library-new/ | Knowledge & Skills
- Industrial Engineering (New) | https://www.shl.com/products/product-catalog/view/industrial-engineering-new/ | Knowledge & Skills
- Informatica (Architecture) (New) | https://www.shl.com/products/product-catalog/view/informatica-architecture-new/ | Knowledge & Skills
- Informatica (Developer) (New) | https://www.shl.com/products/product-catalog/view/informatica-developer-new/ | Knowledge & Skills
- Instrumentation Engineering (New) | https://www.shl.com/products/product-catalog/view/instrumentation-engineering-new/ | Knowledge & Skills
- Interpersonal Communications | https://www.shl.com/products/product-catalog/view/interpersonal-communications/ | Knowledge & Skills
- Interviewing and Hiring Concepts (U.S.) | https://www.shl.com/products/product-catalog/view/interviewing-and-hiring-concepts-u-s/ | Knowledge & Skills
- Java 2 Platform Enterprise Edition 1.4 Fundamental | https://www.shl.com/products/product-catalog/view/java-2-platform-enterprise-edition-1-4-fundamental/ | Knowledge & Skills
- Java 8 (New) | https://www.shl.com/products/product-catalog/view/java-8-new/ | Knowledge & Skills
- Java Design Patterns (New) | https://www.shl.com/products/product-catalog/view/java-design-patterns-new/ | Knowledge & Skills
- Java Frameworks (New) | https://www.shl.com/products/product-catalog/view/java-frameworks-new/ | Knowledge & Skills
- Java Platform Enterprise Edition 7 (Java EE 7) | https://www.shl.com/products/product-catalog/view/java-platform-enterprise-edition-7-java-ee-7/ | Knowledge & Skills
- Java Web Services (New) | https://www.shl.com/products/product-catalog/view/java-web-services-new/ | Knowledge & Skills
- JavaScript (New) | https://www.shl.com/products/product-catalog/view/javascript-new/ | Knowledge & Skills
- Jenkins (New) | https://www.shl.com/products/product-catalog/view/jenkins-new/ | Knowledge & Skills
- Job Control Language (New) | https://www.shl.com/products/product-catalog/view/job-control-language-new/ | Knowledge & Skills
- Kubernetes (New) | https://www.shl.com/products/product-catalog/view/kubernetes-new/ | Knowledge & Skills
- Linux Administration (New) | https://www.shl.com/products/product-catalog/view/linux-administration-new/ | Knowledge & Skills
- Linux Operating System | https://www.shl.com/products/product-catalog/view/linux-operating-system/ | Knowledge & Skills
- Linux Programming (General) | https://www.shl.com/products/product-catalog/view/linux-programming-general/ | Knowledge & Skills
- Load Runner (New) | https://www.shl.com/products/product-catalog/view/load-runner-new/ | Knowledge & Skills
- MFS 360 Enterprise Leadership Report | https://www.shl.com/products/product-catalog/view/mfs-360-enterprise-leadership-report/ | Development & 360
- MFS 360 UCF Group Report | https://www.shl.com/products/product-catalog/view/mfs-360-ucf-group-report/ | Development & 360
- MFS 360 UCF Performance Potential Dev Tips Report | https://www.shl.com/products/product-catalog/view/mfs-360-ucf-performance-potential-dev-tips-report/ | Development & 360
- MFS 360 UCF Standard Report | https://www.shl.com/products/product-catalog/view/mfs-360-ucf-standard-report/ | Development & 360
- MQ Candidate Motivation Report | https://www.shl.com/products/product-catalog/view/mq-candidate-motivation-report/ | Personality & Behavior
- MQ Employee Motivation Report | https://www.shl.com/products/product-catalog/view/mq-employee-motivation-report/ | Personality & Behavior
- MQ Motivation Report Pack | https://www.shl.com/products/product-catalog/view/mq-motivation-report-pack/ | Personality & Behavior
- MQ Profile | https://www.shl.com/products/product-catalog/view/mq-profile/ | Personality & Behavior
- MS Access (New) | https://www.shl.com/products/product-catalog/view/ms-access-new/ | Knowledge & Skills
- MS Excel (New) | https://www.shl.com/products/product-catalog/view/ms-excel-new/ | Knowledge & Skills
- MS Office Basic Computer Literacy (New) | https://www.shl.com/products/product-catalog/view/ms-office-basic-computer-literacy-new/ | Knowledge & Skills
- MS Office Basic Computer Literacy (Sim) (New) | https://www.shl.com/products/product-catalog/view/ms-office-basic-computer-literacy-sim-new/ | Simulations
- MS PowerPoint (New) | https://www.shl.com/products/product-catalog/view/ms-powerpoint-new/ | Knowledge & Skills
- MS Word (New) | https://www.shl.com/products/product-catalog/view/ms-word-new/ | Knowledge & Skills
- Management Scenarios | https://www.shl.com/products/product-catalog/view/management-scenarios/ | Biodata & Situational Judgement
- Managerial Scenarios Candidate Report | https://www.shl.com/products/product-catalog/view/managerial-scenarios-candidate-report/ | Biodata & Situational Judgement
- Managerial Scenarios Narrative Report | https://www.shl.com/products/product-catalog/view/managerial-scenarios-narrative-report/ | Biodata & Situational Judgement
- Managerial Scenarios Profile Report | https://www.shl.com/products/product-catalog/view/managerial-scenarios-profile-report/ | Biodata & Situational Judgement
- Manual Testing (New) | https://www.shl.com/products/product-catalog/view/manual-testing-new/ | Knowledge & Skills
- Manufac. & Indust. - Mechanical & Vigilance 8.0 | https://www.shl.com/products/product-catalog/view/mechanical-and-vigilance-focus-8-0/ | Ability & Aptitude, Personality & Behavior
- Manufac. & Indust. - Safety & Dependability 8.0 | https://www.shl.com/products/product-catalog/view/safety-and-dependability-focus-8-0/ | Personality & Behavior
- Manufacturing & Industrial - Essential Focus 8.0 | https://www.shl.com/products/product-catalog/view/essential-focus-8-0/ | Personality & Behavior
- Manufacturing & Industrial - Mechanical Focus 8.0 | https://www.shl.com/products/product-catalog/view/mechanical-focus-8-0/ | Ability & Aptitude, Personality & Behavior
- Manufacturing & Industrial - Vigilance Focus 8.0 | https://www.shl.com/products/product-catalog/view/vigilance-focus-8-0/ | Ability & Aptitude, Personality & Behavior
- Marketing (New) | https://www.shl.com/products/product-catalog/view/marketing-new/ | Knowledge & Skills
- Maven (New) | https://www.shl.com/products/product-catalog/view/maven-new/ | Knowledge & Skills
- Mechanical Engineering (New) | https://www.shl.com/products/product-catalog/view/mechanical-engineering-new/ | Knowledge & Skills
- Mechatronics Engineering (New) | https://www.shl.com/products/product-catalog/view/mechatronics-engineering-new/ | Knowledge & Skills
- Medical Terminology (New) | https://www.shl.com/products/product-catalog/view/medical-terminology-new/ | Knowledge & Skills
- Metallurgical Engineering (New) | https://www.shl.com/products/product-catalog/view/metallurgical-engineering-new/ | Knowledge & Skills
- Micro Focus Unified Functional Testing (New) | https://www.shl.com/products/product-catalog/view/micro-focus-unified-functional-testing-new/ | Knowledge & Skills
- Microservices (New) | https://www.shl.com/products/product-catalog/view/microservices-new/ | Knowledge & Skills
- Microsoft Dynamics Development (New) | https://www.shl.com/products/product-catalog/view/microsoft-dynamics-development-new/ | Knowledge & Skills
- Microsoft Excel 365 (New) | https://www.shl.com/products/product-catalog/view/microsoft-excel-365-new/ | Knowledge & Skills, Simulations
- Microsoft Excel 365 - Essentials (New) | https://www.shl.com/products/product-catalog/view/microsoft-excel-365-essentials-new/ | Knowledge & Skills, Simulations
- Microsoft Outlook 2013 (adaptive) | https://www.shl.com/products/product-catalog/view/microsoft-outlook-2013-adaptive/ | Knowledge & Skills
- Microsoft PowerPoint 365 - Essentials (New) | https://www.shl.com/products/product-catalog/view/microsoft-powerpoint-365-essentials-new/ | Knowledge & Skills, Simulations
- Microsoft SQL Server 2014 Programming | https://www.shl.com/products/product-catalog/view/microsoft-sql-server-2014-programming/ | Knowledge & Skills
- Microsoft Windows Server 2012 Administration | https://www.shl.com/products/product-catalog/view/microsoft-windows-server-2012-administration/ | Knowledge & Skills
- Microsoft Word 365 (New) | https://www.shl.com/products/product-catalog/view/microsoft-word-365-new/ | Simulations, Knowledge & Skills
- Microsoft Word 365 - Essentials (New) | https://www.shl.com/products/product-catalog/view/microsoft-word-365-essentials-new/ | Knowledge & Skills, Simulations
- Mineral Engineering (New) | https://www.shl.com/products/product-catalog/view/mineral-engineering-new/ | Knowledge & Skills
- Mining Engineering (New) | https://www.shl.com/products/product-catalog/view/mining-engineering-new/ | Knowledge & Skills
- Mobility (New) | https://www.shl.com/products/product-catalog/view/mobility-new/ | Knowledge & Skills
- Molecular Biology (New) | https://www.shl.com/products/product-catalog/view/molecular-biology-new/ | Knowledge & Skills
- MongoDB (New) | https://www.shl.com/products/product-catalog/view/mongodb-new/ | Knowledge & Skills
- Motivation Questionnaire MQM5 | https://www.shl.com/products/product-catalog/view/motivation-questionnaire-mqm5/ | Personality & Behavior
- MuleSoft Development (New) | https://www.shl.com/products/product-catalog/view/mulesoft-development-new/ | Knowledge & Skills
- Multitasking Ability | https://www.shl.com/products/product-catalog/view/multitasking-ability/ | Ability & Aptitude, Knowledge & Skills, Simulations
- Networking and Implementation (New) | https://www.shl.com/products/product-catalog/view/networking-and-implementation-new/ | Knowledge & Skills
- Node.js (New) | https://www.shl.com/products/product-catalog/view/node-js-new/ | Knowledge & Skills
- Nursing (New) | https://www.shl.com/products/product-catalog/view/nursing-new/ | Knowledge & Skills
- OPQ Candidate Plus Report | https://www.shl.com/products/product-catalog/view/opq-candidate-plus-report/ | Personality & Behavior
- OPQ Candidate Report 2.0 | https://www.shl.com/products/product-catalog/view/opq-candidate-report-2-0/ | Personality & Behavior
- OPQ Emotional Intelligence Report | https://www.shl.com/products/product-catalog/view/opq-emotional-intelligence-report/ | Personality & Behavior
- OPQ Leadership Report | https://www.shl.com/products/product-catalog/view/opq-leadership-report/ | Personality & Behavior
- OPQ MQ Sales Report | https://www.shl.com/products/product-catalog/view/opq-mq-sales-report/ | Personality & Behavior
- OPQ Manager Plus Report | https://www.shl.com/products/product-catalog/view/opq-manager-plus-report/ | Personality & Behavior
- OPQ Manager Plus Report 2.0 | https://www.shl.com/products/product-catalog/view/opq-manager-plus-report-2-0/ | Personality & Behavior
- OPQ Maximising your Learning Report | https://www.shl.com/products/product-catalog/view/opq-maximising-your-learning-report/ | Personality & Behavior
- OPQ Premium Plus Report | https://www.shl.com/products/product-catalog/view/opq-premium-plus-report/ | Personality & Behavior
- OPQ Premium Plus Report 2.0 | https://www.shl.com/products/product-catalog/view/opq-premium-plus-report-2-0/ | Personality & Behavior
- OPQ Profile Report | https://www.shl.com/products/product-catalog/view/opq-profile-report/ | Personality & Behavior
- OPQ Team Impact Group Development Report | https://www.shl.com/products/product-catalog/view/opq-team-impact-group-development-report/ | Personality & Behavior
- OPQ Team Impact Individual Development Report | https://www.shl.com/products/product-catalog/view/opq-team-impact-individual-development-report/ | Personality & Behavior
- OPQ Team Impact Selection Report | https://www.shl.com/products/product-catalog/view/opq-team-impact-selection-report/ | Personality & Behavior
- OPQ Team Types & Leadership Styles Profile | https://www.shl.com/products/product-catalog/view/opq-team-types-and-leadership-styles-profile/ | Personality & Behavior
- OPQ Team Types and Leadership Styles Report | https://www.shl.com/products/product-catalog/view/opq-team-types-and-leadership-styles-report/ | Personality & Behavior
- OPQ UCF Development Action Planner Report 1.0 | https://www.shl.com/products/product-catalog/view/opq-ucf-development-action-planner-report/ | Personality & Behavior
- OPQ UCF Development Action Planner Report 2.0 | https://www.shl.com/products/product-catalog/view/opq-ucf-development-action-planner-report-2-0/ | Personality & Behavior
- OPQ Universal Competency Report 1.0 | https://www.shl.com/products/product-catalog/view/opq-universal-competency-report/ | Personality & Behavior
- OPQ Universal Competency Report 2.0 | https://www.shl.com/products/product-catalog/view/opq-universal-competency-report-2-0/ | Personality & Behavior
- OPQ User Report | https://www.shl.com/products/product-catalog/view/opq-user-report/ | Personality & Behavior, Simulations
- OPQ User and Managers Report | https://www.shl.com/products/product-catalog/view/opq-user-and-managers-report/ | Personality & Behavior
- Occupational Personality Questionnaire OPQ32r | https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32r/ | Personality & Behavior
- Operations Management (New) | https://www.shl.com/products/product-catalog/view/operations-management-new/ | Knowledge & Skills
- Oracle DBA (Advanced Level) (New) | https://www.shl.com/products/product-catalog/view/oracle-dba-advanced-level-new/ | Knowledge & Skills
- Oracle DBA (Entry Level) (New) | https://www.shl.com/products/product-catalog/view/oracle-dba-entry-level-new/ | Knowledge & Skills
- Oracle PL/SQL (New) | https://www.shl.com/products/product-catalog/view/oracle-plsql-new/ | Knowledge & Skills
- Oracle WebLogic Server (New) | https://www.shl.com/products/product-catalog/view/oracle-weblogic-server-new/ | Knowledge & Skills
- Organic Chemistry (New) | https://www.shl.com/products/product-catalog/view/organic-chemistry-new/ | Knowledge & Skills
- PHP (New) | https://www.shl.com/products/product-catalog/view/php-new/ | Knowledge & Skills
- PJM Development Report | https://www.shl.com/products/product-catalog/view/pjm-development-report/ | Competencies, Ability & Aptitude, Personality & Behavior
- PJM Selection Report | https://www.shl.com/products/product-catalog/view/pjm-selection-report/ | Ability & Aptitude, Competencies, Personality & Behavior
- Paint Technology (New) | https://www.shl.com/products/product-catalog/view/paint-technology-new/ | Knowledge & Skills
- Pediatrics (New) | https://www.shl.com/products/product-catalog/view/pediatrics-new/ | Knowledge & Skills
- Pega Development (New) | https://www.shl.com/products/product-catalog/view/pega-development-new/ | Knowledge & Skills
- Perl (New) | https://www.shl.com/products/product-catalog/view/perl-new/ | Knowledge & Skills
- Petrochemical Engineering (New) | https://www.shl.com/products/product-catalog/view/petrochemical-engineering-new/ | Knowledge & Skills
- Petroleum Engineering (New) | https://www.shl.com/products/product-catalog/view/petroleum-engineering-new/ | Knowledge & Skills
- Pharmaceutical Analysis (New) | https://www.shl.com/products/product-catalog/view/pharmaceutical-analysis-new/ | Knowledge & Skills
- Pharmaceutical Chemistry (New) | https://www.shl.com/products/product-catalog/view/pharmaceutical-chemistry-new/ | Knowledge & Skills
- Pharmaceutical Science (New) | https://www.shl.com/products/product-catalog/view/pharmaceutical-science-new/ | Knowledge & Skills
- Pharmaceutics (New) | https://www.shl.com/products/product-catalog/view/pharmaceutics-new/ | Knowledge & Skills
- Pharmacology (New) | https://www.shl.com/products/product-catalog/view/pharmacology-new/ | Knowledge & Skills
- Polymer Engineering (New) | https://www.shl.com/products/product-catalog/view/polymer-engineering-new/ | Knowledge & Skills
- Power Electronics and Drives (New) | https://www.shl.com/products/product-catalog/view/power-electronics-and-drives-new/ | Knowledge & Skills
- Power System Engineering (New) | https://www.shl.com/products/product-catalog/view/power-system-engineering-new/ | Knowledge & Skills
- Prism (New) | https://www.shl.com/products/product-catalog/view/prism-new/ | Knowledge & Skills
- Production Engineering (New) | https://www.shl.com/products/product-catalog/view/production-engineering-new/ | Knowledge & Skills
- Production and Industrial Engineering (New) | https://www.shl.com/products/product-catalog/view/production-and-industrial-engineering-new/ | Knowledge & Skills
- Programming Concepts | https://www.shl.com/products/product-catalog/view/programming-concepts/ | Knowledge & Skills
- Project Management (2013) | https://www.shl.com/products/product-catalog/view/project-management-2013/ | Knowledge & Skills
- Proofreading v1 | https://www.shl.com/products/product-catalog/view/proofreading-v1/ | Knowledge & Skills
- Python (New) | https://www.shl.com/products/product-catalog/view/python-new/ | Knowledge & Skills
- R Programming (New) | https://www.shl.com/products/product-catalog/view/r-programming-new/ | Knowledge & Skills
- RESTful Web Services (New) | https://www.shl.com/products/product-catalog/view/restful-web-services-new/ | Knowledge & Skills
- ReactJS (New) | https://www.shl.com/products/product-catalog/view/reactjs-new/ | Knowledge & Skills
- Reading Comprehension - English v1 | https://www.shl.com/products/product-catalog/view/reading-comprehension-english-v1/ | Ability & Aptitude
- Reading Comprehension - Spanish v1 | https://www.shl.com/products/product-catalog/view/reading-comprehension-spanish-v1/ | Ability & Aptitude
- Reading Comprehension v2 | https://www.shl.com/products/product-catalog/view/reading-comprehension-v2/ | Ability & Aptitude
- RemoteWorkQ | https://www.shl.com/products/product-catalog/view/remoteworkq/ | Competencies
- RemoteWorkQ Manager Report | https://www.shl.com/products/product-catalog/view/remoteworkq-manager-report/ | Competencies
- RemoteWorkQ Participant Report | https://www.shl.com/products/product-catalog/view/remoteworkq-participant-report/ | Competencies
- Retail Sales and Service Simulation | https://www.shl.com/products/product-catalog/view/retail-sales-and-service-simulation/ | Biodata & Situational Judgement, Knowledge & Skills, Simulations, Ability & Aptitude
- Reviewing Forms - US (R1) | https://www.shl.com/products/product-catalog/view/reviewing-forms-us-r1/ | Knowledge & Skills
- Ruby (New) | https://www.shl.com/products/product-catalog/view/ruby-new/ | Knowledge & Skills
- Ruby on Rails (New) | https://www.shl.com/products/product-catalog/view/ruby-on-rails-new/ | Knowledge & Skills
- SAP ABAP (Advanced Level) (New) | https://www.shl.com/products/product-catalog/view/sap-abap-advanced-level-new/ | Knowledge & Skills
- SAP ABAP (Intermediate Level) (New) | https://www.shl.com/products/product-catalog/view/sap-abap-intermediate-level-new/ | Knowledge & Skills
- SAP BW (Business Warehouse) (New) | https://www.shl.com/products/product-catalog/view/sap-bw-business-warehouse-new/ | Knowledge & Skills
- SAP Basis (New) | https://www.shl.com/products/product-catalog/view/sap-basis-new/ | Knowledge & Skills
- SAP Business Objects WebI (New) | https://www.shl.com/products/product-catalog/view/sap-business-objects-webi-new/ | Knowledge & Skills
- SAP HCM (Human Capital Management) (New) | https://www.shl.com/products/product-catalog/view/sap-hcm-human-capital-management-new/ | Knowledge & Skills
- SAP Hybris (New) | https://www.shl.com/products/product-catalog/view/sap-hybris-new/ | Knowledge & Skills
- SAP Materials Management (New) | https://www.shl.com/products/product-catalog/view/sap-materials-management-new/ | Knowledge & Skills
- SAP SD (Sales and Distribution) (New) | https://www.shl.com/products/product-catalog/view/sap-sd-sales-and-distribution-new/ | Knowledge & Skills
- SHL Verify Interactive - Inductive Reasoning | https://www.shl.com/products/product-catalog/view/shl-verify-interactive-inductive-reasoning/ | Ability & Aptitude, Simulations
- SHL Verify Interactive G+ | https://www.shl.com/products/product-catalog/view/shl-verify-interactive-g/ | Ability & Aptitude
- SHL Verify Interactive Numerical Calculation | https://www.shl.com/products/product-catalog/view/shl-verify-interactive-numerical-calculation/ | Ability & Aptitude
- SHL Verify Interactive – Deductive Reasoning | https://www.shl.com/products/product-catalog/view/shl-verify-interactive-deductive-reasoning/ | Ability & Aptitude, Simulations
- SHL Verify Interactive – Numerical Reasoning | https://www.shl.com/products/product-catalog/view/shl-verify-interactive-numerical-reasoning/ | Ability & Aptitude, Simulations
- SQL (New) | https://www.shl.com/products/product-catalog/view/sql-new/ | Knowledge & Skills
- SQL Server (New) | https://www.shl.com/products/product-catalog/view/sql-server-new/ | Knowledge & Skills
- SQL Server Analysis Services (SSAS) (New) | https://www.shl.com/products/product-catalog/view/sql-server-analysis-services-%28ssas%29-%28new%29/ | Knowledge & Skills
- SQL Server Integration Services (SSIS) (New) | https://www.shl.com/products/product-catalog/view/sql-server-integration-services-ssis-new/ | Knowledge & Skills
- SQL Server Reporting Services (SSRS) (New) | https://www.shl.com/products/product-catalog/view/sql-server-reporting-services-ssrs-new/ | Knowledge & Skills
- SVAR - Spoken English (AUS) | https://www.shl.com/products/product-catalog/view/svar-spoken-english-aus/ | Simulations
- SVAR - Spoken English (Indian Accent)  (New) | https://www.shl.com/products/product-catalog/view/svar-spoken-english-indian-accent-new/ | Simulations
- SVAR - Spoken English (U.K.) | https://www.shl.com/products/product-catalog/view/svar-spoken-english-u-k/ | Simulations
- SVAR - Spoken English (US)  (New) | https://www.shl.com/products/product-catalog/view/svar-spoken-english-us-new/ | Simulations
- SVAR - Spoken French (Canadian) (New) | https://www.shl.com/products/product-catalog/view/svar-spoken-french-canadian-new/ | Simulations
- SVAR - Spoken French (European) (New) | https://www.shl.com/products/product-catalog/view/svar-spoken-french-european-new/ | Simulations
- SVAR - Spoken Spanish (Castilian) (New) | https://www.shl.com/products/product-catalog/view/svar-spoken-spanish-castilian-new/ | Simulations
- SVAR - Spoken Spanish (North American) (New) | https://www.shl.com/products/product-catalog/view/svar-spoken-spanish-north-american-new/ | Simulations
- Sales & Service Phone Simulation | https://www.shl.com/products/product-catalog/view/sales-and-service-phone-simulation/ | Simulations, Biodata & Situational Judgement
- Sales & Service Phone Solution | https://www.shl.com/products/product-catalog/view/sales-and-service-phone-solution/ | Biodata & Situational Judgement, Personality & Behavior, Simulations
- Sales Interview Guide | https://www.shl.com/products/product-catalog/view/sales-interview-guide/ | Personality & Behavior, Personality & Behavior
- Sales Profiler Cards | https://www.shl.com/products/product-catalog/view/sales-profiler-cards/ | Personality & Behavior
- Sales Transformation 1.0 - Individual Contributor | https://www.shl.com/products/product-catalog/view/sales-transformation-report-individual-contributor/ | Personality & Behavior
- Sales Transformation 2.0 - Individual Contributor | https://www.shl.com/products/product-catalog/view/salestransformationreport2-0-individualcontributor/ | Personality & Behavior
- Sales Transformation Report 1.0 - Sales Manager | https://www.shl.com/products/product-catalog/view/sales-transformation-report-sales-manager/ | Personality & Behavior
- Sales Transformation Report 2.0 - Sales Manager | https://www.shl.com/products/product-catalog/view/sales-transformation-report-2-0-sales-manager/ | Personality & Behavior
- Salesforce Development (New) | https://www.shl.com/products/product-catalog/view/salesforce-development-new/ | Knowledge & Skills
- Search Engine Optimization (New) | https://www.shl.com/products/product-catalog/view/search-engine-optimization-new/ | Knowledge & Skills
- Selenium (New) | https://www.shl.com/products/product-catalog/view/selenium-new/ | Knowledge & Skills
- Shell Scripting (New) | https://www.shl.com/products/product-catalog/view/shell-scripting-new/ | Knowledge & Skills
- Siebel Development (New) | https://www.shl.com/products/product-catalog/view/siebel-development-new/ | Knowledge & Skills
- Smart Interview Live | https://www.shl.com/products/product-catalog/view/smart-interview-live/ | Personality & Behavior
- Smart Interview Live Coding | https://www.shl.com/products/product-catalog/view/smart-interview-live-coding/ | Knowledge & Skills
- Smart Interview On Demand | https://www.shl.com/products/product-catalog/view/smart-interview-on-demand/ | Personality & Behavior
- Social Media (New) | https://www.shl.com/products/product-catalog/view/social-media-new/ | Knowledge & Skills
- Software Business Analysis | https://www.shl.com/products/product-catalog/view/software-business-analysis/ | Knowledge & Skills
- SonarQube (New) | https://www.shl.com/products/product-catalog/view/sonarqube-new/ | Knowledge & Skills
- Spelling (U.S.) (New) | https://www.shl.com/products/product-catalog/view/spelling-u-s-new/ | Knowledge & Skills
- Split Screen Typing Test - Form 1 | https://www.shl.com/products/product-catalog/view/split-screen-typing-test-form-1/ | Ability & Aptitude, Knowledge & Skills
- Spring (New) | https://www.shl.com/products/product-catalog/view/spring-new/ | Knowledge & Skills
- Statistical Analysis System (New) | https://www.shl.com/products/product-catalog/view/statistical-analysis-system-new/ | Knowledge & Skills
- Struts (New) | https://www.shl.com/products/product-catalog/view/struts-new/ | Knowledge & Skills
- Swing (New) | https://www.shl.com/products/product-catalog/view/swing-new/ | Knowledge & Skills
- Tableau (New) | https://www.shl.com/products/product-catalog/view/tableau-new/ | Knowledge & Skills
- Telecommunications Engineering (New) | https://www.shl.com/products/product-catalog/view/telecommunications-engineering-new/ | Knowledge & Skills
- Teradata Development (New) | https://www.shl.com/products/product-catalog/view/teradata-development-new/ | Knowledge & Skills
- Time Management (U.S.) | https://www.shl.com/products/product-catalog/view/time-management-u-s/ | Knowledge & Skills
- Training Development | https://www.shl.com/products/product-catalog/view/training-development/ | Knowledge & Skills
- Typing (New) | https://www.shl.com/products/product-catalog/view/typing-new/ | Simulations
- UNIX (New) | https://www.shl.com/products/product-catalog/view/unix-new/ | Knowledge & Skills
- UiPath RPA Development (New) | https://www.shl.com/products/product-catalog/view/uipath-rpa-development-new/ | Knowledge & Skills
- Universal Competency Framework Interview Guide | https://www.shl.com/products/product-catalog/view/universal-competency-framework-interview-guide/ | Competencies, Personality & Behavior
- Universal Competency Framework Job profiling guide | https://www.shl.com/products/product-catalog/view/universal-competency-framework-job-profiling-guide/ | Competencies, Personality & Behavior
- Universal Competency Framework Profiler Cards (44) | https://www.shl.com/products/product-catalog/view/universal-competency-framework-profiler-cards-44/ | Competencies, Personality & Behavior
- VB.NET (New) | https://www.shl.com/products/product-catalog/view/vb-net-new/ | Knowledge & Skills
- VLSI and Embedded Systems (New) | https://www.shl.com/products/product-catalog/view/vlsi-and-embedded-systems-new/ | Knowledge & Skills
- Verify - Deductive Reasoning | https://www.shl.com/products/product-catalog/view/verify-deductive-reasoning/ | Ability & Aptitude
- Verify - Following Instructions | https://www.shl.com/products/product-catalog/view/verify-following-instructions/ | Ability & Aptitude
- Verify - G+ | https://www.shl.com/products/product-catalog/view/verify-g/ | Ability & Aptitude
- Verify - General Ability Screen | https://www.shl.com/products/product-catalog/view/verify-general-ability-screen/ | Ability & Aptitude
- Verify - Inductive Reasoning (2014) | https://www.shl.com/products/product-catalog/view/verify-inductive-reasoning-2014/ | Ability & Aptitude
- Verify - Numerical Ability | https://www.shl.com/products/product-catalog/view/verify-numerical-ability/ | Ability & Aptitude
- Verify - Technical Checking - Next Generation | https://www.shl.com/products/product-catalog/view/verify-technical-checking-next-generation/ | Ability & Aptitude
- Verify - Verbal Ability - Next Generation | https://www.shl.com/products/product-catalog/view/verify-verbal-ability-next-generation/ | Ability & Aptitude
- Verify - Working with Information | https://www.shl.com/products/product-catalog/view/verify-working-with-information/ | Ability & Aptitude
- Verify G+ - Ability Test Report | https://www.shl.com/products/product-catalog/view/verify-g-ability-test-report/ | Ability & Aptitude
- Verify G+ - Candidate Report | https://www.shl.com/products/product-catalog/view/verify-g-candidate-report/ | Ability & Aptitude
- Verify Interactive Ability Report | https://www.shl.com/products/product-catalog/view/verify-interactive-ability-report/ | Ability & Aptitude
- Verify Interactive G+ Candidate Report | https://www.shl.com/products/product-catalog/view/verify-interactive-g-candidate-report/ | Ability & Aptitude
- Verify Interactive G+ Report | https://www.shl.com/products/product-catalog/view/verify-interactive-g-report/ | Ability & Aptitude
- Verify Interactive Process Monitoring | https://www.shl.com/products/product-catalog/view/verify-interactive-process-monitoring/ | Ability & Aptitude
- Virtual Assessment and Development Centers | https://www.shl.com/products/product-catalog/view/virtual-assessment-and-development-centers/ | Personality & Behavior
- Visual Basic for Applications (New) | https://www.shl.com/products/product-catalog/view/visual-basic-for-applications-new/ | Knowledge & Skills
- Visual Comparison - UK | https://www.shl.com/products/product-catalog/view/visual-comparison-uk/ | Knowledge & Skills
- Visual Comparison - US | https://www.shl.com/products/product-catalog/view/visual-comparison-us/ | Knowledge & Skills
- What Is The Value - US | https://www.shl.com/products/product-catalog/view/what-is-the-value-us/ | Knowledge & Skills
- Workplace Administration Skills (New) | https://www.shl.com/products/product-catalog/view/workplace-administration-skills-new/ | Knowledge & Skills
- Workplace Health and Safety (New) | https://www.shl.com/products/product-catalog/view/workplace-health-and-safety-new/ | Knowledge & Skills
- WriteX - Email Writing (Customer Service) (New) | https://www.shl.com/products/product-catalog/view/writex-email-writing-customer-service-new/ | Simulations
- WriteX - Email Writing (Managerial) (New) | https://www.shl.com/products/product-catalog/view/writex-email-writing-managerial-new/ | Simulations
- WriteX - Email Writing (Sales) (New) | https://www.shl.com/products/product-catalog/view/writex-email-writing-sales-new/ | Biodata & Situational Judgement, Simulations
- Written English v1 | https://www.shl.com/products/product-catalog/view/written-english-v1/ | Knowledge & Skills
- Written Spanish | https://www.shl.com/products/product-catalog/view/written-spanish/ | Knowledge & Skills
- Zabbix (New) | https://www.shl.com/products/product-catalog/view/zabbix-new/ | Knowledge & Skills
- iOS Development (New) | https://www.shl.com/products/product-catalog/view/ios-development-new/ | Knowledge & Skills
- jQuery (New) | https://www.shl.com/products/product-catalog/view/jquery-new/ | Knowledge & Skills"""

SYSTEM_PROMPT = """You are an expert SHL assessment consultant chatbot. Your role is to help HR professionals and hiring managers identify the most appropriate SHL assessments for their job roles and hiring needs.

SHL Individual Test Solutions Catalog (name | url | test_type):
""" + CATALOG_TEXT + """

Test type key:
- Ability & Aptitude: cognitive ability, reasoning, problem-solving
- Biodata & Situational Judgement: real-world scenario judgment, background-based prediction
- Competencies: behavioural competency measurement
- Development & 360: feedback and development tools
- Assessment Exercises: structured exercises and work samples
- Knowledge & Skills: domain-specific knowledge tests (technical, functional, industry)
- Motivation: engagement drivers and motivational fit
- Personality & Behavior: work style, preferences, and personality traits
- Simulations: job simulation assessments

Instructions:
1. Ask clarifying questions about the job role, level (entry/mid/senior/executive), volume of hiring, and key competencies required if not provided.
2. Recommend the most relevant SHL assessments from the catalog above with clear justifications tied to the role requirements.
3. Limit recommendations to 1-5 assessments unless the user asks for more.
4. Always use exact names and URLs from the catalog. Do not invent assessments not in the list.
5. Keep the conversation focused and professional.
6. Indicate end_of_conversation as true only when the user has received their recommendations and signals they are done (e.g., says "thanks", "that's all", "perfect", "goodbye").

IMPORTANT: You MUST respond ONLY with a valid JSON object in this exact format. Do not include any text outside the JSON:
{
  "reply": "Your conversational response here",
  "recommendations": [
    {
      "name": "Assessment Name",
      "description": "Why this assessment fits the role",
      "url": "https://www.shl.com/..."
    }
  ],
  "end_of_conversation": false
}

The "recommendations" list should be empty [] if you are still gathering information. Always include the exact URL from the catalog for each recommended assessment."""

SYSTEM_ACK = json.dumps({
    "reply": "I understand. I am an expert SHL assessment consultant ready to help you identify the right assessments for your hiring needs.",
    "recommendations": [],
    "end_of_conversation": False,
})

_model: Optional[genai.GenerativeModel] = None


def get_model() -> genai.GenerativeModel:
    global _model
    if _model is None:
        api_key = os.environ.get("GEMINI_API_KEY","AIzaSyC8pY9SC9myXoJG5rNopIjhe0VIs3bimRo")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-1.5-flash-latest")
    return _model


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class Recommendation(BaseModel):
    name: str
    description: str
    url: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages list cannot be empty")

    model = get_model()

    contents = [
        {"role": "user", "parts": [{"text": f"[SYSTEM INSTRUCTIONS]\n{SYSTEM_PROMPT}\n\nAcknowledge you understand and are ready to help."}]},
        {"role": "model", "parts": [{"text": SYSTEM_ACK}]},
    ]

    for msg in request.messages:
        role = "model" if msg.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg.content}]})

    try:
        response = model.generate_content(
            contents,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2048,
            ),
        )
        raw_text = response.text or ""
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1]
        raw_text = raw_text.rsplit("```", 1)[0].strip()

    try:
        data = json.loads(raw_text)
        return ChatResponse(
            reply=data.get("reply", ""),
            recommendations=[
                Recommendation(
                    name=r["name"],
                    description=r["description"],
                    url=r.get("url", "https://www.shl.com/solutions/products/product-catalog/"),
                )
                for r in data.get("recommendations", [])
                if isinstance(r, dict) and "name" in r and "description" in r
            ],
            end_of_conversation=bool(data.get("end_of_conversation", False)),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse structured response: {e}\nRaw: {raw_text}")
        return ChatResponse(
            reply=raw_text,
            recommendations=[],
            end_of_conversation=False,
        )
