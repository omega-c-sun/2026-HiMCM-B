#import "template.typ": himcm-setup

#show: himcm-setup

// ----- Page 1: Summary Sheet -----
#include "sections/01_summary.typ"

#pagebreak()

// ----- Contents -----
#set par(first-line-indent: 0pt)
#heading(outlined: false, numbering: none)[Contents]
#outline(title: none, indent: 1.2em, depth: 2)
#set par(first-line-indent: 1.2em)

#pagebreak()

// ----- Body -----
#include "sections/02_intro.typ"
#include "sections/03_restatement.typ"
#include "sections/04_assumptions.typ"
#include "sections/05_methodology.typ"
#include "sections/06_refinements.typ"
#include "sections/07_results.typ"
#include "sections/08_sensitivity.typ"
#include "sections/09_strengths.typ"
#include "sections/10_future.typ"
#include "sections/11_memorandum.typ"
#include "sections/12_blog.typ"

#pagebreak()
#heading(numbering: "1.")[References]
#set par(first-line-indent: 0pt)
#bibliography("refs.yml", title: none, style: "ieee")

#include "sections/13_appendix_code.typ"
