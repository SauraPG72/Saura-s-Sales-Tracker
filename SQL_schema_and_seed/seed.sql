-- adding me as the user
INSERT into users (name, email, password) VALUES('Saura', 'saura@spgcapital.com.au', '$2b$12$XrCxT1p1vsM1CKYLMw5CMu4s/NQbU1QDEhlTkSKNCsc5e6RsZgpM6')

--adding the clients to my user database, just 5 for now 
INSERT into clients (user_id, client_name, company, phone, email, suburb, status) VALUES (1, 'John Do', 'JD Consulting', 0412121212,'john.do@generalassemb.ly', 'Chippendale', 0);

INSERT into clients (user_id, client_name, company, phone, email, suburb, status) VALUES (1, 'Will Sikora', 'Sikora Accountants', 0411111111, 'vasiliisikora@gmail.com', 'Box Hill', 0);

INSERT into clients (user_id, client_name, company, phone, email, suburb, status) VALUES (1, 'Vyomma Bhaskar', 'Bhaskar Financial Advisers', 0422222222, 'vyomaa03@gmail.com', 'Cragieburn', 1);

INSERT into clients (user_id, client_name, company, phone, email, suburb, status) VALUES (1, 'Garmon Weng', 'Garmon and Co Wealth Advisory', 0433333333, 'garmonweng@gmail.com', 'East Hills', 0);

INSERT into clients (user_id, client_name, company, phone, email, suburb, status) VALUES (1, 'Sarah So', 'So Good Home Loans', 0444444444, 'mrs.sarahso@gmail.com', 'Sydney', 1);