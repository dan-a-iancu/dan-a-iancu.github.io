---
title: Research
type: landing

sections:
  # Order: the scannable area panels lead, followed by the complete research-profile
  # discussion and then the topic filter immediately above the lists it acts on. The
  # word cloud remains on the home page.
  - block: markdown
    content:
      title: ""
      text: |-
        ### Research Interests

        <div class="rp-areas">
        <div class="rp-area">

        #### Methodological

        - Optimization under uncertainty
        - Robust optimization
        - Data-driven optimization
        - Fairness in analytics and AI

        </div>
        <div class="rp-area">

        #### Application areas

        - Global supply chain management — commodity supply chains, food systems
        - FinTech — supply chain financing, asset management, risk management
        - Healthcare — chronic disease management, public policy

        </div>
        </div>
    design:
      columns: "1"

  - block: markdown
    content:
      title: ""
      text: |-
        My research asks how individuals and organizations can make better decisions in
        complex operational systems—and how analytics and AI can improve not only
        performance, but also resilience, fairness, and social and environmental outcomes.

        I work across two closely connected streams. The first develops methods for
        decision-making under uncertainty, including robust, adaptive, and data-driven
        optimization. I am particularly interested in methods that remain tractable,
        transparent, and fair when information is incomplete and conditions change. The
        second uses these methods, together with economic modeling and empirical data,
        to design better operational systems, incentives, and contracts.

        Much of my applied work focuses on global supply chains and responsible
        operations: improving smallholder livelihoods, reducing child and forced labor,
        protecting forests, strengthening supply-chain resilience, expanding access to
        clean technologies, and reducing waste. I also study problems at the
        intersections of operations with finance, healthcare, and public policy. Across
        these domains, the common goal is to use analytics and AI to design decisions
        and systems that work better for organizations, individuals, and society.
    design:
      columns: "1"

  - block: topic-filter
    content:
      title: Browse by topic
      text: |-
        Filter the lists below by research theme. Papers often belong to more than one;
        tick "match all selected" to see only those at the intersection.

  - block: collection
    content:
      title: Journal Publications
      count: 0
      order: desc
      filters:
        folders: ["publications"]
        publication_type: "article-journal"
    design:
      view: citation-summary

  - block: collection
    content:
      title: Under Review
      count: 0
      order: desc
      filters:
        folders: ["publications"]
        publication_type: "article"
    design:
      view: citation-summary

  - block: collection
    content:
      title: Working Papers and Active Research
      count: 0
      order: desc
      filters:
        folders: ["publications"]
        publication_type: "manuscript"
    design:
      view: citation-summary

  - block: collection
    content:
      title: Other Publications
      count: 0
      order: desc
      filters:
        folders: ["publications"]
        publication_type: "chapter"
    design:
      view: citation-summary

  - block: collection
    content:
      title: Peer-Reviewed Conference Papers (Selection)
      count: 0
      order: desc
      filters:
        folders: ["publications"]
        publication_type: "paper-conference"
    design:
      view: citation-summary

  - block: collection
    content:
      title: Theses
      count: 0
      order: desc
      filters:
        folders: ["publications"]
        publication_type: "thesis"
    design:
      view: citation-summary

  # Aggregated honors section — DISABLED at the owner's request (it read oddly on this
  # page). The `awards-compact` block, the author `awards[]` data (12 entries) and the
  # per-paper award lines all remain in place, so re-enabling is just uncommenting this.
  # - block: awards-compact
  #   content:
  #     title: Honors and awards
  #     username: admin
---
