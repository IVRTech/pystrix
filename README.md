pystrix is an attempt at creating a versatile [Asterisk](http://www.asterisk.org/)-interface package for AMI and (Fast)AGI needs. It is published as an open-source library under the LGPLv3 by [Ivrnet, inc.](http://www.ivrnet.com/), welcoming contributions from all users.

---

# Overview #
pystrix runs on [Python](http://python.org/) 2.6+ (intended to be compatible with Python 3.x with the 2to3 script), on any platform. It's targeted at Asterisk 1.10 and provides a rich, easy-to-extend set of bindings for AGI, FastAGI, and AMI.

# Release schedule #
pystrix is expected to reach 1.0.0 status around the beginning of July, 2013, with a 1.10.0 release expected very shortly after that, following an audit of Asterisk 1.10's AMI and AGI interfaces to ensure consistency. At this time, the first downloadable releases will be made available. 0.9.6 (the current code in the repository) should be stable, but if you need to use this library for production purposes, stick with 0.9.4 for now, since 0.9.6 has seen some significant changes and has not been battle-hardened.

After 1.10.0, all future releases will follow Asterisk's version-numbering scheme for the first two digits, to help avoid confusion when determining compatibility, meaning that 1.11.0 will be compatible with Asterisk 11's new features, and so forth.

# History #
After some research, we found that what was available was either incompatible with the architecture model we needed to work with ([Twisted](http://www.twistedmatrix.org/), while excellent for a great many things, isn't always the right choice), was targeting an outdated version of Asterisk, or had a very rigid, monolithic design. Identifying the [pyst](http://pyst.sourceforge.net/) and [py-asterisk](http://code.google.com/p/py-asterisk/) packages as being similar, but structurally incompatible, to what we wanted, pyst was chosen as the basis for this project, with a full rewrite of its AGI and AMI systems to provide a uniform-looking, highly modular design that incorporates logic and ideas from py-asterisk. The end result is a package that should satisfy anyone who was looking at either of its ancestors and that should be easier to extend as Asterisk continues to evolve.

# Usage #
Detailed usage information is provided in the documentation, along with simple examples that should help to get anyone started.

## Documentation ##
Every release will be packaged with full offline HTML documentation, which is the preferred way to look things up.

Online documentation is available at http://static.uguu.ca/projects/pystrix/doc/, but please use the offline version when possible, since the online documentation is unstable and may not be available when you need it most.

Inline documentation is complete and made readable by [reStructuredText](http://docutils.sourceforge.net/rst.html), so you'll never be completely lost.


---

# Credits #
[Ivrnet, inc.](http://www.ivrnet.com/)
  * Initial development of pystrix was funded by Ivrnet
  * Ivrnet is a software-as-a-service company that develops and operates intelligent software applications, delivered through traditional phone networks and over the Internet. These applications facilitate automated interaction, personalized communication between people, mass communication for disseminating information to thousands of people concurrently, and personalized communication between people and automated systems. Ivrnet's applications are accessible through nearly any form of communication technology, at any time, from anywhere in North America, via voice, phone, fax, email, texting, and the Internet.

[Neil Tallim](http://uguu.ca/)
  * Development lead
  * Programming
