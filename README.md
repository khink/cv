cv
==

Assumptions
-----------

A1) The Resume's layout and looks will be changed manually before sending.
A2) The Resume will be sent as a PDF.
A3) We have a Generic Resume which will contain all information.
    This can contain lots of detail.
    From Generic, we created a tailored Resume which filters out the details
    that are less relevant to the job application at hand.
A4) The Generic resume should be easy to edit, as this is the main place
    for editing.

Nice to have:

A5) There should be an easy way to create a tailored Resume from the
    Generic.
A6) There should be an easy way to keep a translation of (parts of) the
    Generic Resume.
A7) The Generic Resume should be kept under Version Control in a sane manner.


Conclusions
-----------

A1) Resume could be marked up in LibreOffice.
    LibreOffice OTOH, is a complete mess, layout-wise.
A2)
A4) speaks against keeping the Generic in XML, unless we find a real
    friendly XML editor.
    It speaks for Markdown or Restructured Text.

A5) and A6) speak for XML, with tags for detail filters and translations.