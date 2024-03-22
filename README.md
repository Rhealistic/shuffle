#DELEGATED CURATIONS

##FEATURE: SHUFFLE
Serves as a calendar management tool streamlining and automating repetitive curatorial processes.

##TERMINOLOGIES
- `Concept`: A recurring curation such as an event running every week at a certain space/venue.
- `Opportunity`: Performance slots for artists
- `Subscribers`: Artists signed up to be part of a rotation for securing an opportunity.

##HOW SHUFFLE WORKS
Upon subscription, each artist will go through the following statuses through the cycle.

`POTENTIAL` - Artists who join the concept through a form into the database.
`NEXT UP` - Artist selected by Shuffle for the next performance.
`PERFORMED` - One who has used the opportunity successfully.
`NEXT CYCLE` - One who has utilized or skipped an opportunity.

Then, two algorithms will run,

A Discovery algorithm
The Shuffle algorithm.
The discovery algorithm runs first, weekly (currently set to Mondays) which discovers opportunities (Looks for subscribers and subscriptions to each concept)
Then each subscriber will acquire a tag based on the artists actions once an invite is sent to them via SMS

The Opportunity Status
`ACCEPTED` - One who takes the opportunity in time.
`SKIP` - One who rejects the opportunity
`EXPIRED` - One who did not answer the opportunity and hasn’t replied in time
`AWAITING_ACCEPTANCE` - One whose response is being awaited after an opportunity has been sent
`PENDING` - One who hasn’t been picked before for an opportunity.

The shuffle criteria:
- One has no pending requests. Has replied (accepted) an opportunity before.
- They have performed in this concept in the past (x) weeks.
- The algorithm will not give the opportunity to one who has already performed recently. The curator chooses how long that would be.
- Has not skipped an opportunity in (x) weeks.
- Not expired in the (x) weeks.
- Skipped in the past (x) weeks.

Then Shuffle runs after for those who meet the criteria and are shuffled, and an artist is selected.