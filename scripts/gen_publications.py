#!/usr/bin/env python3
"""Generate Hugo publication page bundles for the academic site.

NON-DESTRUCTIVE BY DESIGN: writes only to build/pub-staging/ and never to
content/.  Promote with scripts/promote_publications.sh after review.

Data below is authored from two sources, per AGENTS.md locked decisions:
  * bibliographic fields  -> the publisher record
    (docs/reference/crossref-reconciliation.md, generated from Crossref)
  * everything else       -> current-website-jemdoc/research.jemdoc
    (awards, press, online companions, code, prior circulated titles)

Neither research.jemdoc nor assets/publications.bib is reliable alone; they are
wrong about different entries.  See the reconciliation doc.

Stdlib only.  Idempotent: rerunning reproduces identical output.
"""
import os, re, shutil, sys

JEMDOC = "/Users/daniancu/Library/CloudStorage/Dropbox/Academic/Sites/new-site/current-website-jemdoc"
OUT    = "build/pub-staging"

ME = "Dan A. Iancu"   # replaced by `admin` on emit so the theme links the author page

# ---------------------------------------------------------------- data --------
# date: drives sort + the year shown by the citation view.  Vary the MONTH to
# control order inside a group; only the year is ever displayed.  NEVER use a
# future date -- buildFuture is false in production, so the page would vanish.
PUBS = [
  # ============================== THESES ==============================
  dict(slug="phd-thesis-adaptive-robust-optimization",
       summary='A doctoral thesis on making robust optimization work when decisions unfold over time rather than all at once. It develops adaptive policies that respond to uncertainty as it is observed while remaining computationally tractable, and applies them to inventory and revenue management.',
       title="Adaptive Robust Optimization with Applications in Inventory and Revenue Management",
       authors=[ME], date="2010-06-01",
       publication="Ph.D. Thesis, [Massachusetts Institute of Technology](http://www.mit.edu)",
       types=["thesis"], pdf="Papers/phd_thesis.pdf"),

  dict(slug="bs-thesis-geometric-quantum-information",
       summary='An undergraduate thesis approaching quantum information geometrically. If the state of n qubits lives in a high-dimensional complex space, what do the natural symmetric structures in that space look like? It develops an algorithm for constructing analogues of the Platonic solids there — uniform Hilbertian polytopes — as a step toward measuring entanglement.',
       title="Geometric Approach to Digital Quantum Information. Quantum Entanglement",
       authors=[ME], date="2004-05-01",
       publication="B.S. Thesis, [Yale University](http://www.yale.edu)",
       types=["thesis"], pdf="Papers/quant_thesis.pdf"),

  # ========================= OTHER PUBLICATIONS =======================
  dict(slug="financial-access-or-price-premiums",
       summary='Smallholder households growing commodities such as cocoa often depend on their children’s labor to secure basic subsistence. We model their borrowing, saving, consumption, and child-labor decisions and uncover sharp trade-offs: better credit access can reduce or increase child labor depending on why a household borrows; better savings access consistently reduces child labor but can lower consumption; and price premiums reduce child labor only when sufficiently large, otherwise they may increase it. Effective interventions must therefore be tailored to household circumstances.',
       title="Financial Access or Price Premiums? A Nuanced View into Improving Farmer Welfare and Reducing Child Labor in Commodity Supply Chains",
       authors=["André Calmon","Andreas Gernert",ME,"Luk N. Van Wassenhove"],
       date="2024-02-01",
       publication="Book chapter in *Responsible and Sustainable Operations: The New Frontier*, Springer Series in Supply Chain Management, vol. 24, pp. 145–159",
       types=["chapter"], pdf="Papers/Other/Cocoa_Book_Chapter.pdf"),

  dict(slug="robust-multistage-decision-making",
       summary='Decisions under uncertainty often unfold over time, so a useful plan must preserve the ability to adapt as new information arrives. This tutorial provides a unified view of robust multistage decision-making: the distinction between static, fully adaptive, and partially adjustable decisions; why exact solutions become intractable; connections with robust dynamic programming; when simple policies can work well or even be optimal; how time-consistency problems arise; and how the framework is used in applications.',
       title="Robust Multi-stage Decision Making",
       authors=["Erick Delage",ME], date="2015-01-01",
       publication="*TutORials in Operations Research: The Operations Research Revolution*, pp. 20–46, INFORMS",
       types=["chapter"], pdf="Papers/Other/tutorial-multistage-RO.pdf",
       links=[("slides","Other/INFORMS_Tutorial_RMSDM.pdf","Presentation slides")]),

  # ==================== PEER-REVIEWED CONFERENCE ======================
  dict(slug="linear-policies-drlq-control-neurips-2025",
       summary='How much distributional ambiguity can classical LQG control absorb? Across a broad family of divergence-based uncertainty sets, we prove that the worst-case noise distribution remains Gaussian and that a policy linear in the observations remains optimal. The adversary responds to uncertainty by inflating the noise covariance rather than shifting its mean. These structural results preserve the familiar form of LQG control even when the noise distribution is not known precisely.',
       title="Optimality of Linear Policies in Distributionally Robust Linear Quadratic Control",
       authors=["Bahar Taşkesen",ME,"Çağil Koçyiğit","Daniel Kuhn"], date="2025-12-01",
       publication="*Advances in Neural Information Processing Systems* (NeurIPS)",
       types=["paper-conference"],
       pdf="Papers/Conference/Linear_Policies_DRLQG_NeurIPS_2025.pdf"),

  dict(slug="distributionally-robust-lq-control-neurips-2023",
       summary='Classical LQG control assumes the distribution of the noise is known. We instead allow any distribution within a Wasserstein ball around a Gaussian estimate, including non-Gaussian distributions, and optimize against the worst case. Despite this ambiguity, a policy that is linear in the observations remains optimal. An efficient numerical method uses the Frank-Wolfe algorithm to find the least-favorable distributions and Kalman filtering to compute the controller.',
       awards=[dict(text='Spotlight presentation (3.06% of 12,343 submissions)', year='2023')],
       title="Distributionally Robust Linear Quadratic Control",
       authors=["Bahar Taşkesen",ME,"Çağil Koçyiğit","Daniel Kuhn"], date="2023-12-01",
       publication="*Advances in Neural Information Processing Systems* (NeurIPS)",
       types=["paper-conference"],
       pdf="Papers/Conference/Distributionally_Robust_Linear_Quadratic_Control_NeurIPS_2023.pdf",
       body="> [!NOTE]\n> Accepted as a spotlight presentation (3.06% of 12,343 submissions)."),

  dict(slug="power-generation-management-time-varying",
       summary='Utilities linked by transmission lines must dispatch a changing mix of generators to meet demand as both loads and renewable supply vary over time. We formulate a multi-period dispatch model that accounts for the cost of adjusting generation between periods and derive an efficient solution method. Under conditions often encountered in practice, the solution is globally optimal; numerical experiments quantify the benefits of adjusting thermal generation at finer time scales.',
       title="Power Generation Management Under Time-Varying Power and Demand Conditions",
       authors=["Soumyadip Ghosh",ME,"Dmitriy Katz-Rogozhnikov","Dzung T. Phan","Mark S. Squillante"],
       date="2011-07-01",
       publication="*Proceedings of the IEEE Power & Energy Society General Meeting*, pp. 1–7",
       types=["paper-conference"], doi="10.1109/PES.2011.6039781",
       pdf="Papers/Conference/MultiOPF_Conf.pdf"),

  dict(slug="affine-policies-multistage-robust-cdc-2009",
       summary='Multistage robust control becomes intractable as the horizon grows, so the field leans on policies that respond affinely to observed disturbances — a practical restriction usually assumed to cost something. For one-dimensional, box-constrained problems with convex state costs and linear control costs, we prove those affine policies are exactly optimal. The argument comes from polyhedral geometry rather than dynamic programming, and yields fast algorithms when the state costs are piecewise affine.',
       title="Optimality of Affine Policies in Multi-stage Robust Optimization",
       authors=["Dimitris Bertsimas",ME,"Pablo A. Parrilo"], date="2009-12-01",
       publication="*Proceedings of the 48th IEEE Conference on Decision and Control (CDC)*, pp. 1131–1138",
       types=["paper-conference"], doi="10.1109/CDC.2009.5399533",
       pdf="Papers/Conference/cdc09_final_ver.pdf"),

  # ============================ UNDER REVIEW ==========================
  # publication_types "article" renders as "Preprint" via the theme's i18n.
  # There is no CSL type for "submitted"/"under review"; the review status is
  # carried in the `publication` string, as it is on the jemdoc page.
  dict(slug="stable-profitable-trading-platforms",
       summary='Digital platforms connecting smallholder farmers and intermediaries promise traceability and better livelihoods, but participants may return to informal networks if the platform provides too little value. Combining an optimization model with data from Indonesia’s palm-oil supply chain, we find that profitability depends critically on controlling transportation costs and learning at least part of the informal network. Payments should go primarily to farmers, and minimum-cost matching is usually best—except when unusually well-connected intermediaries must be prioritized to keep the platform stable.',
       title="Stable and Profitable Trading Platforms for Smallholder Commodity Supply Chains",
       authors=["Sergio Camelo-Gomez","Joann F. de Zegher",ME], date="2025-09-01",
       publication="Major revision at *Manufacturing & Service Operations Management*",
       types=["article"],
       pdf="Papers/Working/Stable_Platforms/Stable-and-Profitable-Trading-Platforms-for-Smallholder-Commodity-Supply-Chains.pdf"),

  dict(slug="optimality-linear-policies-drlq-control",
       summary='We generalize LQG control to a broad family of ambiguity sets around a nominal Gaussian distribution. The worst-case distribution is itself Gaussian, with zero mean and an inflated covariance, and the optimal controller remains linear in the observations. These structural results yield a Frank-Wolfe algorithm that outperforms semidefinite-programming reformulations and extend to infinite-horizon control; under Wasserstein ambiguity, they also hold for elliptical nominal distributions.',
       awards=[dict(text='Finalist, INFORMS George Nicholson Student Paper Competition (B. Taşkesen)', year='2023')],
       title="Optimality of Linear Policies in Distributionally Robust Linear Quadratic Control",
       authors=["Bahar Taşkesen",ME,"Çağil Koçyiğit","Daniel Kuhn"], date="2025-10-01",
       publication="Major revision at *Management Science*",
       types=["article"],
       pdf="Papers/Working/Affine_LQG/Optimality-of-Linear-Policies-in-Distributionally-Robust-LQ-Control.pdf",
       body=("Some of this material appeared in a preliminary conference paper entitled\n"
             "*\u201cDistributionally Robust Linear Quadratic Control\u201d*.\n\n"
             "> [!NOTE]\n"
             "> Finalist for the INFORMS George Nicholson Student Paper Competition\n"
             "> (B. Taşkesen, 2023).")),

  dict(slug="area-conditions-positive-incentives",
       summary='Millions of smallholder farmers grow the world’s commodities, and some clear forest to expand their farms and escape poverty. We compare individual incentives with two collective designs: area no-deforestation, which rewards farmers if no forest is cleared, and a new “area no-use” condition, which rewards them if no one earns income from recently deforested land. Which approach works best depends on local cooperation, the cost and reliability of blocking forest use, and whether every farmer must be compensated.',
       awards=[dict(text='Winner, SAWIT Challenge, USAID & Indonesia Business Council for Sustainable Development', year='2016'), dict(text='Finalist, INFORMS George Nicholson Student Paper Competition (J. de Zegher)', year='2018')],
       title="Area Conditions and Positive Incentives: Engaging Local Communities to Protect Forests",
       authors=["Xavier Warnes","Joann de Zegher",ME,"Erica L. Plambeck"], date="2025-12-01",
       publication="Major revision at *Management Science*",
       types=["article"],
       pdf="Papers/Working/Area_Conditions/Area-Conditions-and-Positive-Incentives-Engaging-Local-Communities-to-Protect-Forests.pdf",
       links=[("source","Papers/Working/Area_Conditions/Jdz_DI_EP_Pay_Delay.pdf","Original paper"),
              ("source","Papers/Working/Area_Conditions/Jdz_DI_EP_Pay_Delay_ec.pdf","Original e-companion")],
       body=("Some of this material appeared in a previous paper entitled *\u201cSustaining\n"
             "Smallholders and Rainforests by Eliminating Payment Delay in a Commodity Supply\n"
             "Chain — It Takes a Village\u201d*.\n\n"
             "> [!NOTE]\n"
             "> Winner, SAWIT Challenge, USAID & Indonesia Business Council for Sustainable\n"
             "> Development (2016).\n"
             ">\n"
             "> Finalist for the INFORMS George Nicholson Student Paper Competition\n"
             "> (J. de Zegher, 2018).")),

  dict(slug="optimized-targeted-confinements-pandemic",
       summary='During COVID-19, many governments confined people differently by age or activity, but the value of such targeting was contested. We develop a framework that balances mortality against lost economic output and apply it to Île-de-France. Targeting by either age or activity improves on uniform policies, while targeting by both improves on either dimension alone. These gains persist when epidemiological parameters are uncertain and can even increase with greater ambiguity.',
       title="Optimized Targeted Confinements for Future Pandemic Response",
       authors=["Sergio Camelo-Gomez","Dragos F. Ciocan",ME,"Xavier Warnes","Spyros I. Zoumpoulis"],
       date="2025-11-01",
       publication="Major revision at *Operations Research*",
       types=["article"],
       pdf="Papers/Working/Pandemic_Control/Optimized-Targeted-Confinements-for-Future-Pandemic-Response.pdf",
       body=("Previously circulated as *\u201cQuantifying and Realizing the Benefits of Targeting\n"
             "for Pandemic Response\u201d*.")),

  # ================= WORKING PAPERS AND ACTIVE RESEARCH ===============
  # Titles here come from research.jemdoc, which is NEWER than the .bib: five of
  # these eight have since been retitled and the .bib still has the old names.
  # There is no publisher record to arbitrate, so jemdoc wins (locked decision 1).
  dict(slug="child-labor-operational-lever",
       summary='More than 1.5 million children work in cocoa production in Côte d’Ivoire and Ghana, despite decades of intervention. We model child labor as one of the levers smallholder households use to balance production, consumption, and finances under harvest uncertainty. The analysis identifies three forces—resource relief, labor productivity, and consumption expansion—that explain why the same program may reduce child labor for some households and increase it for others. Descriptive survey evidence from an NGO partner in Ghana is consistent with the framework, which shows how observable household characteristics can help target interventions.',
       title="Child Labor as an Operational Lever: Heterogeneous Effects of Interventions in Cocoa Supply Chains",
       authors=["André Calmon","Andreas K. Gernert",ME,"Luca Andrei Manea"], date="2026-01-01",
       publication="Major revision at *Manufacturing & Service Operations Management*",
       types=["article"],
       pdf="Papers/Working/Child_Labor/Child_Labor_in_Cocoa_Heterogeneous_Effects.pdf"),

  dict(slug="payments-for-ecosystem-services",
       title="Payments for Ecosystem Services: Balancing Upfront and Ex-Post Payments to Overcome Financial Barriers",
       authors=["Itai Ashlagi",ME,"Zhuoyang Liu"], date="2025-12-01",
       publication="Working paper, in preparation for submission to *Management Science*",
       types=["manuscript"]),

  dict(slug="identifying-forced-labor",
       title="Identifying Forced Labor in the Construction and Food Industries",
       authors=["Antonio Torres-Skillikorn","Sarah Billington",ME], date="2025-11-01",
       publication="Working paper, in preparation for submission", types=["manuscript"]),

  dict(slug="inventory-for-impact-clean-cooking",
       title="Inventory for Impact: Scalable Inventory Routing for Clean Cooking Access in Developing Economies",
       authors=["Sergio Camelo-Gomez",ME,"Maximilian Schiffer","Simon Thoma"], date="2025-10-01",
       publication="Work in progress", types=["manuscript"]),

  dict(slug="supply-chain-intermediation-clean-cooking",
       title="Supply Chain Intermediation for Clean Cooking Solutions",
       authors=[ME,"Ömer Karaduman"], date="2025-09-01",
       publication="Work in progress", types=["manuscript"]),

  dict(slug="dynamic-incentives-smallholder-welfare",
       awards=[dict(text='Winner, SAWIT Challenge, USAID & Indonesia Business Council for Sustainable Development', year='2016'), dict(text='Finalist, INFORMS George Nicholson Student Paper Competition (J. de Zegher)', year='2018')],
       title="Dynamic Incentives for Improving Smallholder Welfare and Protecting Forests",
       authors=["Xavier Warnes",ME,"Erica L. Plambeck"], date="2025-08-01",
       publication="Work in progress", types=["manuscript"],
       links=[("source","Papers/Working/Area_Conditions/Jdz_DI_EP_Pay_Delay.pdf","Original paper"),
              ("source","Papers/Working/Area_Conditions/Jdz_DI_EP_Pay_Delay_ec.pdf","Original e-companion")],
       body=("Some of this material appeared in a previous paper entitled *\u201cSustaining\n"
             "Smallholders and Rainforests by Eliminating Payment Delay in a Commodity Supply\n"
             "Chain — It Takes a Village\u201d*.\n\n"
             "> [!NOTE]\n"
             "> Winner, SAWIT Challenge, USAID & Indonesia Business Council for Sustainable\n"
             "> Development (2016).\n"
             ">\n"
             "> Finalist for the INFORMS George Nicholson Student Paper Competition\n"
             "> (J. de Zegher, 2018).")),

  dict(slug="ai-solutions-sustainable-protein-choices",
       title="AI Solutions for Incentivizing Sustainable Protein Choices in Diets",
       authors=["Antoine Desir",ME,"Felipe Vizzoto"], date="2025-07-01",
       publication="Work in progress", types=["manuscript"]),

  dict(slug="nurse-staffing-strategic-labor-pools",
       title="Nurse Staffing with Strategic Labor Pools",
       authors=["Yue Hu",ME,"Saniya Vaidya","Zhuoyang Liu"], date="2025-05-01",
       publication="Work in progress", types=["manuscript"]),

  dict(slug="price-of-funding-inflexibility",
       title="The Price of Funding Inflexibility in Humanitarian Operations",
       authors=["Thomas Breugem","Ece Gürserliler",ME,"Luk N. Van Wassenhove"], date="2025-06-01",
       publication="Work in progress", types=["manuscript"]),

  # ======================= JOURNAL PUBLICATIONS =======================
  # Bibliographic fields are the PUBLISHER record (Crossref); see
  # docs/reference/crossref-reconciliation.md.  Note two consequences:
  #   * Titles use publisher hyphenation ("Multistage", "Multitier"), which is
  #     what Scholar and Crossref match against, though both of Dan's sources
  #     hyphenate.
  #   * "Boosting Sales" and "Dynamic Pricing under Debt" and "Is Operating
  #     Flexibility Harmful Under Debt?" were all "articles in advance" on the
  #     jemdoc page and have since appeared in print.  Using their real years
  #     necessarily reorders the group relative to jemdoc -- see MIGRATION.md.
  # `date` month is the issue number as a proxy, so `order: desc` gives true
  # reverse chronology.
  dict(slug="boosting-sales-premade-foods",
       summary='A grocer selling premade food must decide how long items stay on the shelf, whether to sell the freshest or the oldest first, whether to timestamp them, and how to price. In our base model, the best policy is counterintuitive: sell the freshest item first and do not timestamp, which can extend shelf life, increase sales, and reduce waste. Model extensions identify conditions that favor selling the oldest item first and show how customer heterogeneity can make timestamps valuable.',
       title="Boosting Sales and Customer Welfare from Premade Foods (Let the Freshest Chicken Fly off the Shelf First)",
       authors=[ME,"Jae-Hyuck Park","Erica L. Plambeck"], date="2026-04-01",
       publication="*Management Science*, vol. 72, no. 4, pp. 2937–2954",
       types=["article-journal"], doi="10.1287/mnsc.2022.01246",
       pdf="Papers/Journal/17.Boosting_Sales/Boosting-Sales-and-Customer-Welfare-from-Premade-Foods.pdf",
       links=[('source', 'Papers/Journal/17.Boosting_Sales/Boosting-Sales-and-Customer-Welfare-from-Premade-Foods_ec.pdf', 'Online companion')],
       body='Previously circulated as *“On the Management of Premade Foods”*.'),

  dict(slug="climate-impacts-digital-use-supply-chains",
       summary='Accounts of technology’s climate footprint usually count the emissions from building, shipping, and operating devices. We introduce digital use supply chains—the production and resource consumption recorded or enabled by everyday digital activity—and use moment-by-moment Screenomics data to connect individual behavior with emissions. In a single-case study, one day of behavior-related emissions is estimated to be roughly 1,000 times the device’s own life-cycle emissions, suggesting opportunities for personalized feedback and behavior-change programs.',
       title="Climate impacts of digital use supply chains",
       authors=["Lin Shi","Adam Brandt",ME,"Katharine Mach","Christopher Field","Moon-Jung Cho","S. Chey","Nilam Ram","Todd Robinson","Byron Reeves"],
       date="2024-01-01",
       publication="*Environmental Research: Climate*, vol. 3, no. 1, 015009",
       types=["article-journal"], doi="10.1088/2752-5295/ad22eb",
       pdf="Papers/Journal/16.Digital_Use/Climate_Impact_Digital_Use_Supply_Chains.pdf"),

  dict(slug="monitoring-with-limited-information",
       summary='Sometimes a decision maker must choose when to stop a treatment or trade while being able to observe its state only a few times. We develop a robust-optimization approach that jointly chooses when to monitor and when to stop. Under certain conditions, fixed monitoring times achieve the same worst-case reward as fully adaptive ones, making the dynamic policy much easier to compute. Applied to monitoring heart-transplant patients, the approach substantially improves on current recommendations.',
       title="Monitoring with Limited Information",
       authors=[ME,"Nikolaos Trichakis","Do Young Yoon"], date="2021-07-01",
       publication="*Management Science*, vol. 67, no. 7, pp. 4233–4251",
       types=["article-journal"], doi="10.1287/mnsc.2020.3736",
       pdf="Papers/Journal/14.Monitoring/monitoring_limited_info.pdf",
       links=[('source', 'Papers/Journal/14.Monitoring/monitoring_limited_info_ec.pdf', 'Online companion')]),

  dict(slug="value-loss-allocation-systems-provider-guarantees",
       summary='Many systems allocate tasks centrally to providers whose welfare depends on what they receive, creating a tension between provider guarantees and total value. We derive tight bounds on the value lost when such guarantees are imposed and show that the loss is limited. With many providers, fairness is the main driver; with few, differences in providers’ effectiveness matter more. When providers are identical, the loss never exceeds 50%, and experiments with real and synthetic data find much smaller losses in several practical settings.',
       title="Value Loss in Allocation Systems with Provider Guarantees",
       authors=["Yonatan Gur",ME,"Xavier Warnes"], date="2021-06-01",
       publication="*Management Science*, vol. 67, no. 6, pp. 3757–3784",
       types=["article-journal"], doi="10.1287/mnsc.2020.3656",
       pdf="Papers/Journal/15.Value_Loss/Value-Loss-Allocation-Systems-Provider-Guarantees.pdf",
       links=[("code", "Papers/Journal/15.Value_Loss/code.zip", "Replication code")]),

  dict(slug="loyalty-program-liabilities-and-point-values",
       summary='Loyalty points are a currency the firm issues, and the future service they promise appears on its balance sheet as a liability. We show that the optimal total value of outstanding points should track the firm’s “profit potential”—realized cash flows plus deferred revenue. Point values rise with stronger operating performance and greater uncertainty, allowing loyalty programs to buffer fluctuations in future performance and providing a rationale for them beyond marketing or competition.',
       title="Loyalty Program Liabilities and Point Values",
       authors=["So Yeon Chun",ME,"Nikolaos Trichakis"], date="2020-02-01",
       publication="*Manufacturing & Service Operations Management*, vol. 22, no. 2, pp. 257–272",
       types=["article-journal"], doi="10.1287/msom.2018.0748",
       pdf="Papers/Journal/13.Loyalty_programs/loyalty_programs.pdf",
       links=[('source', 'Papers/Journal/13.Loyalty_programs/loyalty_programs_ec.pdf', 'Online companion')],
       body='Previously circulated as *“Points for Peanuts or Peanuts for Points? Dynamic Management of a Loyalty Program”*.'),

  dict(slug="designing-contracts-sourcing-channels-shared-value",
       awards=[dict(text='Finalist, M&SOM Journal Best Paper Prize', year='2021 and 2022'), dict(text='Second place, Best Student Paper in Supply Chain Management, POMS Society (Joann de Zegher)', year='2016')],
       title="Designing Contracts and Sourcing Channels to Create Shared Value",
       authors=["Joann F. de Zegher",ME,"Hau L. Lee"], date="2019-02-01",
       publication="*Manufacturing & Service Operations Management*, vol. 21, no. 2, pp. 271–289",
       types=["article-journal"], doi="10.1287/msom.2017.0627",
       pdf="Papers/Journal/12.Contracts_Sourcing_Channels/contracts_sourcing_channels.pdf",
       links=[('source', 'Papers/Journal/12.Contracts_Sourcing_Channels/contracts_sourcing_channels-ec.pdf', 'Online companion')],
       summary=('When a new farming technology helps the buyer but costs the farmer, adoption depends on how the two sides trade. We study when changing the contract, switching from commodity sourcing to direct sourcing, or combining both can turn a one-sided innovation into a mutual gain. The answer hinges on how the technology’s costs scale. Using farm data from Patagonia, Argentina, we estimate that the proposed mechanism could increase average supply-chain profit by 6.9% while also producing environmental benefits.'),
       body="{{< paper-awards >}}"),

  dict(slug="dynamic-pricing-under-debt",
       summary='Firms often borrow to finance inventory, then price that inventory both to earn a profit and to service the debt. We show limited liability leads such sellers to charge higher prices and discount more slowly, and that these distortions compound over time into a downward performance spiral. We then quantify how much of the loss practical debt covenants can recover.',
       title="Dynamic Pricing Under Debt: Spiraling Distortions and Efficiency Losses",
       authors=["Omar Besbes",ME,"Nikolaos Trichakis"], date="2018-10-01",
       publication="*Management Science*, vol. 64, no. 10, pp. 4572–4589",
       types=["article-journal"], doi="10.1287/mnsc.2017.2862",
       pdf="Papers/Journal/11.Pricing_Debt/pricing_debt.pdf",
       links=[('source', 'Papers/Journal/11.Pricing_Debt/pricing_debt-ec.pdf', 'Online companion')]),

  dict(slug="dynamic-learning-patient-response-types",
       summary='Many chronic-disease medications work only for a subgroup of patients, and no biomarker identifies that subgroup in advance. We develop an adaptive treatment framework that learns from both continuous measures of disease progression and the timing and severity of infrequent events such as relapses, helping physicians decide when to persist and when to stop. Applied to interferon treatment for multiple sclerosis, the resulting policies provide a cost-effectiveness frontier and benchmarks for existing treatment guidelines.',
       awards=[dict(text='Finalist, INFORMS Health Applications William Pierskalla Best Paper Award', year='2014', url='https://www.informs.org/Recognizing-Excellence/Community-Prizes/Health-Applications-Society/Pierskalla-Best-Paper-Award')],
       title="Dynamic Learning of Patient Response Types: An Application to Treating Chronic Diseases",
       authors=["Diana M. Negoescu","Kostas Bimpikis","Margaret L. Brandeau",ME], date="2018-08-01",
       publication="*Management Science*, vol. 64, no. 8, pp. 3469–3488",
       types=["article-journal"], doi="10.1287/mnsc.2017.2793",
       pdf="Papers/Journal/09.Learning_response/dynamic_learning_response.pdf",
       links=[('source', 'Papers/Journal/09.Learning_response/dynamic_learning_response-ec.pdf', 'Online companion')],
       body=("> [!NOTE]\n"
             "> Finalist for the [INFORMS Health Applications William Pierskalla Best\n"
             "> Paper Award](https://www.informs.org/Recognizing-Excellence/Community-Prizes/Health-Applications-Society/Pierskalla-Best-Paper-Award) (2014).")),

  dict(slug="disruption-risk-optimal-sourcing-multitier",
       summary='A manufacturer worried about disruptions at its suppliers’ suppliers usually cannot choose those tier-2 firms directly, but it can shape their selection through contracts with tier 1. When tier-1 suppliers share tier-2 sources in a diamond-shaped network, the manufacturer should rely less on excess inventory and multisourcing and more on inducing tier-1 mitigation. Yet manufacturers prefer less overlap while tier-1 suppliers may prefer more; penalty contracts can alleviate this conflict.',
       awards=[dict(text='Finalist, MSOM Interface of Finance, Operations and Risk Management Best Paper Award', year='2019', url='https://www.informs.org/Recognizing-Excellence/Community-Prizes/Manufacturing-and-Service-Operations-Management/MSOM-iFORM-SIG-Best-Paper-Award')],
       title="Disruption Risk and Optimal Sourcing in Multitier Supply Networks",
       authors=["Erjie Ang",ME,"Robert Swinney"], date="2017-08-01",
       publication="*Management Science*, vol. 63, no. 8, pp. 2397–2419",
       types=["article-journal"], doi="10.1287/mnsc.2016.2471",
       pdf="Papers/Journal/08.Disruption_Risk/disruption_networks.pdf",
       links=[('source', 'Papers/Journal/08.Disruption_Risk/disruption_networks-ec.pdf', 'Online companion')],
       body=("> [!NOTE]\n"
             "> Finalist for the [MSOM Interface of Finance, Operations and Risk\n"
             "> Management Best Paper Award](https://www.informs.org/Recognizing-Excellence/Community-Prizes/Manufacturing-and-Service-Operations-Management/MSOM-iFORM-SIG-Best-Paper-Award) (2019).")),

  dict(slug="is-operating-flexibility-harmful-under-debt",
       summary='Operating flexibility is normally an asset, but under debt it can invite risk-shifting — and we find the resulting borrowing costs can erase more than a third of a firm’s value. We then ask whether the covenants lenders actually write can restore it. Simple financial covenants suffice when the firm can liquidate inventory mid-season; richer forms of flexibility demand more.',
       awards=[dict(text='Winner, MSOM Interface of Finance, Operations and Risk Management Best Paper Award', year='2018', url='https://www.informs.org/Recognizing-Excellence/Community-Prizes/Manufacturing-and-Service-Operations-Management/MSOM-iFORM-SIG-Best-Paper-Award')],
       title="Is Operating Flexibility Harmful Under Debt?",
       authors=[ME,"Nikolaos Trichakis","Gerry Tsoukalas"], date="2017-06-01",
       publication="*Management Science*, vol. 63, no. 6, pp. 1730–1761",
       types=["article-journal"], doi="10.1287/mnsc.2015.2415",
       pdf="Papers/Journal/10.Inventory_Flexibility_Debt/ops_flexibility_debt.pdf",
       links=[("site", "https://www.gsb.stanford.edu/insights/should-your-bank-be-allowed-micromanage-your-business", "Stanford Business Insights")],
       body=('Previously circulated as *“Operationalizing Financial Covenants”*.\n\n'
             "> [!NOTE]\n"
             "> Winner of the [MSOM Interface of Finance, Operations and Risk\n"
             "> Management Best Paper Award](https://www.informs.org/Recognizing-Excellence/Community-Prizes/Manufacturing-and-Service-Operations-Management/MSOM-iFORM-SIG-Best-Paper-Award) (2018).")),

  dict(slug="tight-approximations-dynamic-risk-measures",
       summary='There are two natural ways to measure risk across many periods: apply a single risk measure to the total future cost, or compose one-step risk mappings. We characterize when one always dominates the other and introduce a metric for how far apart they are. An asymmetry emerges — the tightest upper bound admits an exact characterization, while the lower bound does not.',
       title="Tight Approximations of Dynamic Risk Measures",
       authors=[ME,"Marek Petrik","Dharmashankar Subramanian"], date="2015-03-01",
       publication="*Mathematics of Operations Research*, vol. 40, no. 3, pp. 655–682",
       types=["article-journal"], doi="10.1287/moor.2014.0689",
       pdf="Papers/Journal/05.Tight_Approx_Risk/approx_dynamic_risk.pdf"),

  dict(slug="fairness-efficiency-multiportfolio-optimization",
       summary='A manager running many client accounts cannot treat them independently: trades move prices, so executing one account affects the others. We develop a tractable method that jointly optimizes all trades and divides the resulting market-impact costs across accounts, allowing the manager to balance aggregate gains with equitable treatment. Numerical studies indicate that the approach outperforms methods commonly used in industry or proposed in prior research.',
       title="Fairness and Efficiency in Multiportfolio Optimization",
       authors=[ME,"Nikolaos Trichakis"], date="2014-06-01",
       publication="*Operations Research*, vol. 62, no. 6, pp. 1285–1301",
       types=["article-journal"], doi="10.1287/opre.2014.1310",
       pdf="Papers/Journal/06.Multiaccount/multiaccount.pdf",
       links=[('source', 'Papers/Journal/06.Multiaccount/multiaccount_ec.pdf', 'Online companion'),
              ("site", "https://www.gsb.stanford.edu/insights/dan-iancu-tapping-moral-philosopher-solve-money-managers-dilemma", "Stanford Business Insights")]),

  dict(slug="pareto-efficiency-in-robust-optimization",
       summary='Robust optimization protects you against the worst case — but in doing so it often leaves performance on the table when the worst case does not materialize. Two decisions can be identical under the worst case while one is better in every other scenario. We show how to find the robust decisions that are not dominated this way, at essentially no additional cost.',
       awards=[dict(text='Winner, INFORMS Optimization Society Young Researchers Prize', year='2018', url='https://connect.informs.org/optimizationsociety/prizes/young-researchers-prize'), dict(text='First place, INFORMS JFIG Paper Competition', year='2013', url='https://www.informs.org/Recognize-Excellence/Community-Prizes-and-Awards/Junior-Faculty-Interest-Group/Junior-Faculty-Forum-Paper-Competition')],
       title="Pareto Efficiency in Robust Optimization",
       authors=[ME,"Nikolaos Trichakis"], date="2014-01-01",
       publication="*Management Science*, vol. 60, no. 1, pp. 130–147",
       types=["article-journal"], doi="10.1287/mnsc.2013.1753",
       pdf="Papers/Journal/07.Pareto_RO/PRO.pdf",
       body=("> [!NOTE]\n"
             "> Winner of the [INFORMS Optimization Society Young Researchers\n"
             "> Prize](https://connect.informs.org/optimizationsociety/prizes/young-researchers-prize) (2018).\n"
             ">\n"
             "> First place in the [INFORMS JFIG Paper Competition](https://www.informs.org/Recognize-Excellence/Community-Prizes-and-Awards/Junior-Faculty-Interest-Group/Junior-Faculty-Forum-Paper-Competition) (2013).")),

  dict(slug="supermodularity-affine-policies-dynamic-robust",
       summary='Two classical approaches to dynamic robust optimization rarely meet: dynamic programming, which is exact but intractable, and simple decision rules, which are tractable but usually approximate. We give conditions — uncertainty sets that are integer sublattices of the unit hypercube, plus a technical condition — under which affine decision rules are exactly optimal, bridging the two.',
       title="Supermodularity and Affine Policies in Dynamic Robust Optimization",
       authors=[ME,"Mayank Sharma","Maxim Sviridenko"], date="2013-04-01",
       publication="*Operations Research*, vol. 61, no. 4, pp. 941–956",
       types=["article-journal"], doi="10.1287/opre.2013.1172",
       pdf="Papers/Journal/04.Supermod_Affine/supermod_robust.pdf",
       links=[('source', 'Papers/Journal/04.Supermod_Affine/supermod_robust_online_companion.pdf', 'Online companion')]),

  dict(slug="new-local-search-algorithm-binary-optimization",
       summary='Local search for binary optimization normally trades solution quality against running time with no principled way to set the dial. We develop a general-purpose algorithm whose single parameter controls both the depth of the search and its computational cost. The method has a formal approximation guarantee for a class of set-packing problems and, on large randomly generated set-covering and set-packing instances, performs competitively with leading general-purpose optimization software.',
       title="A New Local Search Algorithm for Binary Optimization",
       authors=["Dimitris Bertsimas",ME,"Dmitriy Katz-Rogozhnikov"], date="2013-02-01",
       publication="*INFORMS Journal on Computing*, vol. 25, no. 2, pp. 208–221",
       types=["article-journal"], doi="10.1287/ijoc.1110.0496",
       pdf="Papers/Journal/03.Local_Search_Binary/IJOC_IPpaper.pdf"),

  dict(slug="hierarchy-near-optimal-policies-multistage-adaptive",
       summary='Multistage decisions under uncertainty are usually attacked with simple policy classes, because the exact problem is intractable. We introduce a hierarchy of polynomial disturbance-feedback policies, each computable from a single semidefinite program and indexed by the polynomial’s degree. Raising the degree buys accuracy at a predictable computational price.',
       title="A Hierarchy of Near-Optimal Policies for Multistage Adaptive Optimization",
       authors=["Dimitris Bertsimas",ME,"Pablo A. Parrilo"], date="2011-12-01",
       publication="*IEEE Transactions on Automatic Control*, vol. 56, no. 12, pp. 2809–2824",
       types=["article-journal"], doi="10.1109/TAC.2011.2162878",
       pdf="Papers/Journal/02.Polynomial_Policies/polynomial_param.pdf"),

  dict(slug="optimality-affine-policies-multistage-robust",
       summary='Multistage robust optimization is generally intractable, so the field relies on policies that depend affinely on observed disturbances — a restriction adopted for convenience and assumed to be suboptimal. For one-dimensional, constrained problems with convex state costs and linear control costs, we prove affine policies are exactly optimal. The proof turns on the geometry of the feasible set rather than dynamic programming.',
       awards=[dict(text='Best Student Paper Prize, INFORMS Optimization Society', year='2009', url='http://connect.informs.org/optimizationsociety/prizes/students-prize')],
       title="Optimality of Affine Policies in Multistage Robust Optimization",
       authors=["Dimitris Bertsimas",ME,"Pablo A. Parrilo"], date="2010-02-01",
       publication="*Mathematics of Operations Research*, vol. 35, no. 2, pp. 363–394",
       types=["article-journal"], doi="10.1287/moor.1100.0444",
       pdf="Papers/Journal/01.Affine_Policies/affine_policies_RO.pdf",
       body=("> [!NOTE]\n"
             "> [Best Student Paper Prize](http://connect.informs.org/optimizationsociety/prizes/students-prize) of the INFORMS Optimization\n"
             "> Society (2009).")),
]


# ---------------------------------------------------------------- topics -------
TOPICS_FILE = "data/paper-topics.yaml"

def load_topics():
    """Parse data/paper-topics.yaml with the stdlib only.

    Deliberately not PyYAML: this script must run for the site owner without
    installing anything. The file's shape is fixed and documented in its header,
    so a focused parser is safer than an unavailable dependency.

    Returns (names: code -> display name, assignments: slug -> [codes]).
    """
    if not os.path.isfile(TOPICS_FILE):
        return {}, {}
    text = open(TOPICS_FILE, encoding="utf-8").read()
    head, _, body = text.partition("\npapers:")
    names = {}
    for code, block in re.findall(r"^  (\w+):\n((?:    .*\n)+)", head, re.M):
        m = re.search(r"^    name:\s*(.+?)\s*$", block, re.M)
        if m:
            names[code] = m.group(1).strip().strip("'\"")
    assign = {}
    for slug, codes in re.findall(r"^  ([a-z0-9][a-z0-9-]+):\s*\[([^\]]*)\]", body, re.M):
        assign[slug] = [c.strip() for c in codes.split(",") if c.strip()]
    return names, assign

# ---------------------------------------------------------------- emit --------
def yaml_str(v):
    return '"' + v.replace('\\','\\\\').replace('"','\\"') + '"'

def emit(p):
    d = os.path.join(OUT, p["slug"])
    os.makedirs(d, exist_ok=True)
    fm = ["---", f"title: {yaml_str(p['title'])}", "authors:"]
    for a in p["authors"]:
        fm.append("  - admin" if a == ME else f"  - {yaml_str(a)}")
    fm += [f"date: {p['date']}", f"publishDate: {p['date']}",
           f"publication: {yaml_str(p['publication'])}",
           "publication_types: [" + ", ".join(yaml_str(t) for t in p["types"]) + "]"]
    # `abstract` drives the metadata row the theme labels via i18n. We relabel that
    # row to "Summary" in i18n/en.yaml and put a short plain-language summary here
    # rather than the paper's formal abstract.
    if p.get("summary"):
        fm.append(f"abstract: {yaml_str(p['summary'])}")
    if p.get("doi"):
        fm += ["hugoblox:", "  ids:", f"    doi: {yaml_str(p['doi'])}"]
    links = []
    if p.get("pdf"):
        links.append(("pdf", os.path.basename(p["pdf"]), None))
    for t, src, label in p.get("links", []):
        # external URLs pass through verbatim; local paths are copied into the bundle
        links.append((t, src if src.startswith("http") else os.path.basename(src), label))
    if links:
        fm.append("links:")
        for t, url, label in links:
            fm.append(f"  - type: {t}")
            fm.append(f"    url: {yaml_str(url)}")
            if label:
                fm.append(f"    label: {yaml_str(label)}")
    if p.get("awards"):
        fm.append("awards:")
        for a in p["awards"]:
            fm.append(f"  - text: {yaml_str(a['text'])}")
            fm.append(f"    year: {yaml_str(a['year'])}")
            if a.get("url"):
                fm.append(f"    url: {yaml_str(a['url'])}")
    # "N min read" is meaningless on a paper stub (single.html:102 gates on this)
    if p.get("topics"):
        fm.append("topics: [" + ", ".join(yaml_str(t) for t in p["topics"]) + "]")
    # "N min read" is meaningless on a paper stub (single.html:102 gates on this)
    fm += ["reading_time: false", "featured: false", "tags: []", "---"]

    body = p.get("body", "")
    # Awards are rendered by the `paper-awards` shortcode from the `awards` front
    # matter, never as prose. Strip any legacy `> [!NOTE]` callout (the theme's
    # generic blue information panel, which was both visually heavy and mislabelled)
    # and append the shortcode instead. Prose such as "previously circulated as"
    # notes is preserved.
    if p.get("awards"):
        body = re.sub(r'> \[!NOTE\]\n(?:>.*\n?)*', '', body).rstrip()
        body = (body + "\n\n" if body else "") + "{{< paper-awards >}}"
    # Topic links last: single.html renders only the publication_type term, so
    # without this the topics taxonomy is unreachable from a paper page.
    if p.get("topics"):
        body = (body + "\n\n" if body else "") + "{{< paper-topics >}}"
    open(os.path.join(d, "index.md"), "w").write("\n".join(fm) + ("\n\n" + body + "\n" if body else "\n"))

    # copy bundle assets out of the read-only jemdoc tree
    assets = ([p["pdf"]] if p.get("pdf") else []) + \
            [s for _, s, _ in p.get("links", []) if not s.startswith("http")]
    for src in assets:
        s = os.path.join(JEMDOC, src)
        if not os.path.isfile(s):
            print(f"  !! MISSING ASSET {src}", file=sys.stderr); continue
        shutil.copy2(s, os.path.join(d, os.path.basename(src)))
    return d

if __name__ == "__main__":
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    topic_names, topic_assign = load_topics()

    # Fail loudly on drift between the topics file and PUBS. A mistyped code or a
    # renamed slug would otherwise just silently drop a paper out of every filter.
    unknown_codes = {c for codes in topic_assign.values() for c in codes} - set(topic_names)
    assert not unknown_codes, f"{TOPICS_FILE}: undeclared topic codes {sorted(unknown_codes)}"
    slugs = {p["slug"] for p in PUBS}
    stale = set(topic_assign) - slugs
    assert not stale, f"{TOPICS_FILE}: slugs not in PUBS {sorted(stale)}"
    missing = slugs - set(topic_assign)
    if missing:
        print(f"  note: {len(missing)} paper(s) absent from {TOPICS_FILE}: {sorted(missing)}",
              file=sys.stderr)

    for p in PUBS:
        p["topics"] = [topic_names[c] for c in topic_assign.get(p["slug"], [])]

    seen = set()
    for p in PUBS:
        assert p["slug"] not in seen, f"duplicate slug {p['slug']}"
        seen.add(p["slug"])
        assert p["date"] <= "2026-09-05", f"future date on {p['slug']}"
        emit(p)
    print(f"staged {len(PUBS)} publications to {OUT}/")
