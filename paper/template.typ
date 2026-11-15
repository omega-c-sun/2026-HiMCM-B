// HiMCM 2026 Problem B — shared typography & helpers
// Control Number 18388

#let team-number = "18388"
#let problem-choice = "B"

#let himcm-setup(body) = {
  set page(
    paper: "us-letter",
    margin: (top: 1in, bottom: 1in, left: 1in, right: 1in),
    header: context {
      if counter(page).get().first() > 1 [
        #set text(size: 10pt, font: "Times New Roman")
        Team \##team-number — Page #counter(page).display()
        #h(1fr)
        Problem #problem-choice
        #v(-0.35em)
        #line(length: 100%, stroke: 0.4pt)
      ]
    },
    footer: none,
  )
  set text(font: "Times New Roman", size: 12pt, lang: "en")
  set par(justify: true, leading: 0.7em, first-line-indent: 1.2em)
  set heading(numbering: "1.1")
  show heading.where(level: 1): it => {
    set par(first-line-indent: 0pt)
    set text(size: 14pt, weight: "bold")
    v(0.85em)
    it
    v(0.4em)
  }
  show heading.where(level: 2): it => {
    set par(first-line-indent: 0pt)
    set text(size: 12pt, weight: "bold")
    v(0.6em)
    it
    v(0.25em)
  }
  show heading.where(level: 3): it => {
    set par(first-line-indent: 0pt)
    set text(size: 12pt, style: "italic", weight: "regular")
    v(0.45em)
    it
    v(0.15em)
  }
  set figure(gap: 0.65em)
  show figure.caption: set text(size: 10pt)
  show math.equation: set text(font: "Times New Roman")
  set list(indent: 1.2em)
  set enum(indent: 1.2em)
  body
}

#let summary-header = {
  set par(first-line-indent: 0pt)
  set align(center)
  text(size: 11pt)[*Team Control Number*]
  linebreak()
  text(size: 20pt, weight: "bold")[#team-number]
  v(0.35em)
  text(size: 11pt)[*Problem Chosen*]
  linebreak()
  text(size: 18pt, weight: "bold")[#problem-choice]
  v(0.45em)
  text(size: 14pt, weight: "bold")[2026 HiMCM/MidMCM Summary Sheet]
  v(0.55em)
  line(length: 100%, stroke: 0.6pt)
  v(0.45em)
}

#let no-indent(body) = {
  set par(first-line-indent: 0pt)
  body
}
