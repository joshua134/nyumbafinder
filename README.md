# NyumbaFinder KE – Kenya’s Most Trusted House-Hunting Platform

> **"No more fake listings. No more scammers. Only verified homes."**

Finding a house in Nairobi can be difficult, expensive and risky – especially for students, people with disabilities, or anyone affected by bad weather. Landlords and agents often post fake listings, disappear with deposits, or waste people’s time.

**NyumbaFinder KE solves this forever.**

### Core Features
- Post bedsitters, 1-bedroom, 2-bedroom, 3-bedroom, studio apartments, double rooms etc.
- Listings include:
  - House photos (multiple)
  - Exact location & house number
  - Floor number & floor
  - Rent, deposit, rental terms
  - Landlord/agent contact

- Renters can **rate and review** previous houses and landlords
- Powerful search & filters using ratings, price, location and house type

### 6-Layer Anti-Scammer System (The Fortress)

| # | Protection Layer                        | How It Works
---|------------------------------------------|---------------------------------------------------------------
1  | **ID & Business Verification**           | National ID / Business registration / tenancy agreement required
2  | **Payment Barrier**                      | KES 800 M-Pesa STK Push required before listing goes live
3  | **Manual Admin Approval**           | Every single listing is reviewed and approved by admins
4  | **Auto-Delete Inactive Listings**        | If listing fee not paid in 3–4 months → listing + account deleted
5  | **User Reviews & Ratings**               | Previous renters expose dishonest landlords publicly
6  | **Report & Permanent Ban**               | Users report fake listings → repeat offenders banned forever

> Result: **Only genuine, serious landlords and agents** can post. Scammers are blocked at every step.

### Entities & Security
- **User**: first name, last name, email, phone, **encrypted National ID/Passport**, role (renter/landlord/agent)
- **House Listing**: title, type, location, rent, deposit, house number, floor, images, terms, status (pending/approved)
- **Review**: rating (1–5), comment, reviewer name/email
- All sensitive data encrypted or hashed

### Tech Stack
- Backend: Python Django
- Database: PostgreSQL + Redis (caching)
- Frontend: Tailwind CSS + Flowbite + Leaflet.js (interactive map)
- Payments: M-Pesa Daraja API (STK Push – KES 800)
- Hosting: Railway / Render / PythonAnywhere
- Authentication: Django Allauth + email verification
- Admin Panel: Custom + Django Admin (secret URL)

### Project Status
**Fully Functional MVP – Live Demo Available**  
**Anti-scammer system 100% implemented**  
**Ready for scaling across Kenya & East Africa**

### Screenshots
![Post House Form](screenshots/post-house.png)
![Verified Listing](screenshots/house-detail.png)
![Admin Approval Panel](screenshots/admin-panel.png)
![M-Pesa STK Push](screenshots/mpesa-stk.png)

### Future Improvements (Agile Roadmap)
- Video tours upload
- Virtual viewing calendar
- Agent verification badge
- Swahili & local languages
- Mobile app (React Native)

### Contributors
- Website Implementation & Full-Stack Code
- Database Design & Security
- Ethics, UX & Anti-Scammer Architecture
- Testing & Presentation

> **NyumbaFinder KE – Built to protect Kenyan families from housing scams.**

**Live Demo**: https://nyumbafinder.up.railway.app  
**Secret Admin Panel**: `/nyumba-secret-panel-2025/`

---
**“We don’t just list houses. We verify trust.”**
