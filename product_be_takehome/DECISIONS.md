# Decisions

Keep this to one page. We weight it as heavily as the code.

## End user

Who do you believe uses this dashboard, and what do they use it to
decide? Everything below should follow from this answer.

## Claim modeling

The feed is remit-level; your `/claims` endpoint is claim-level. What
judgment calls did you make getting from one to the other, and why?
Frame the "why" around your end user: what would they want to see,
and what would mislead them?

## Storage

SQLite or MongoDB — which did you pick, and why that one for this data?
How do you handle re-ingesting on restart? What would you have done
differently with more than 2-3 hours?

## API design

Why these response shapes? What did you leave out, and why?

## Testing

What did you assert in `tests/test_api.py`, and what did you deliberately
leave untested in the time you had?

## AI usage

What did you have AI generate? What did it get wrong or gloss over?
What did you verify yourself, and how?
