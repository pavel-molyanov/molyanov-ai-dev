# Business Rules

## Purpose
Domain-specific business logic, workflows, and validation rules. Only fill if project has complex domain rules that are not obvious from code.

---

<!--
WHEN TO USE THIS FILE:

Use this file if your project has:
- Multi-step workflows with state transitions
- Complex validation rules that depend on business context
- Formulas or calculations with business meaning
- Domain-specific constraints not captured in database schema

WHEN NOT TO USE:

Skip this file if your project is:
- Simple CRUD application
- Utility tool or CLI
- Internal tool with obvious logic
- Project where all logic is self-explanatory from code

If not needed, DELETE THIS FILE or write "N/A - no complex business logic"

---

EXAMPLES OF WHAT BELONGS HERE:

## Multi-step Workflows

order status flow:
pending → paid → shipped → delivered

Rules:
- Can cancel if status = pending or paid (before shipping)
- Can't cancel after shipped
- Refund: full if pending, partial if paid, none if shipped

---

## Validation Rules

booking constraints:
- Must cancel 24h before appointment to get refund
- Max 4 people per booking
- Can't double-book same email within 7 days
- Booking window: 1-90 days in advance

payment constraints:
- Minimum order: $10
- Maximum order: $5000 (without KYC verification)

---

## Calculations/Formulas

pricing formula:
final_price = (subtotal - discount) * (1 + tax_rate) + shipping

Rules:
- Discount applies BEFORE tax
- Free shipping if subtotal > $50
- Tax rate depends on billing address state

commission formula:
commission = sales * commission_rate
- Standard: 10%
- Premium: 5%
- Enterprise: 3%

---

## State Machines

user subscription lifecycle:
trial (7 days) → active → cancelled → grace_period (3 days) → expired

Transitions:
- trial → active: on successful payment
- active → cancelled: user cancels, access until period end
- cancelled → grace_period: payment failed, retry 3 times
- grace_period → active: payment succeeds
- grace_period → expired: all retries failed

---

## Access Control (if complex)

feature access by tier:
- Free: 10 projects max, basic features
- Pro: unlimited projects, API access, priority support
- Enterprise: custom limits, SSO, dedicated support

content visibility:
- Draft: only author can see
- Published: all authenticated users
- Private: author + explicitly shared users

---

DELETE ABOVE EXAMPLES and write your project-specific rules below.
Keep it concise - only rules that agents need to know to write correct code.

-->
