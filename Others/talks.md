software updater attacks

difficult attack vector to protect

updates are inevitable, updates must be practical, but updates are dangerous



must update to fix security issues.

insecure update mechanism is a new security problem



example: security of automobile. canvas is a very weak machanism which can be compromised easily in network. 

cars are dangerous:

- researchers have made some scary attacks against vehicles

- cars are multi-ton, fast-moving weapons.



how to address security concers:

- prevent: make it harder for a compromise to occur

- detect: detect incidents of compromise quickly

  most automative technologies

- transfer risk: have inserance or claim regulations were followed

  -100Ms USD lawsuit likely unachievable

- mitigate: make a succesful compromise less impactful

  major uptane value add



update basics: repostitory <-- client



- inadequate update seciruty 3: TLS/SSL

-  4: Just Sign
  - traditional solution2: sign your update package with a specifiv key; updater ships with corresponding public key. client has to trudt this key. 
  - but this key can be stolen, attackers can install arbitray code on any client

goal: 

- to survive server compromise tiwht the minumum pssible damage

-  avoid arbitray pacjage attacks

-  minimize damage of a single key biding exposed

- Be able to revoke keys, maintaing trust

-  guarantee freshness to avoid freeze attacks

-  prevent mix and match attacks

- ...



Design principles 

- separation of duties
- threshold signatures
- explicit and implicit revocation of keys



updatane an open and secure SOTA system

Upatane srandardization: open, community standardization effort

Security designs

upatne integration



we want to avoid: some groups will elect to use insecure designs; companies that do not secure their cars put in danger.



uptane.github.io