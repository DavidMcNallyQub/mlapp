/*
    INSERT COMMANDS
*/
-- INSERT a user.
INSERT INTO users (email, password)
VALUES ("d@e.com","pbkdf2:sha256:260000$CzTzWa93psg47Zqx$45bde5d45e55fa280411243aaf060a12f1d49ee7149ee6ea49929b38f4e0d8b2");
-- INSERT the inital users.
INSERT INTO users (email, password)
VALUES ("d@e.com","pbkdf2:sha256:260000$CzTzWa93psg47Zqx$45bde5d45e55fa280411243aaf060a12f1d49ee7149ee6ea49929b38f4e0d8b2"),
("dmcnally16@qub.ac.uk","pbkdf2:sha256:260000$CzTzWa93psg47Zqx$45bde5d45e55fa280411243aaf060a12f1d49ee7149ee6ea49929b38f4e0d8b2");
-- INSERT initial classifications.
INSERT INTO classification (classification)
VALUES ("Misinformation"), ("Neutral"); 
-- INSERT an issue.
INSERT INTO issue (comment, date_created, issue, author_id, classified_id)
VALUES ("This is a comment.", "This addresses the comment.","2023-01-20 01:23:45", 1, 2);
-- INSERT inital issues.
INSERT INTO issue (comment, date_created, issue, author_id, classification_id)
VALUES ("This is a comment.", "This addresses the comment.","2023-01-20 01:23:45", 1, 1),
("This is another comment.", "This addresses the other comment.","2023-01-22 06:07:08", 1, 2),
("This is a comment.", "This addresses the comment.","2023-01-23 09:00:00", 2, 1);
-- INSERT a parent.
INSERT INTO parents (name)
VALUES ("Seamus");
-- INSERT a child.
INSERT INTO children (name, owner_id)
VALUES ("David", "Seamus");
-- INSERT an owner.
INSERT INTO owners (name, fullname)
VALUES ("Seamus", "D Mcnally");
-- INSERT a pet.
INSERT INTO pets (name, owner_id)
VALUES ("Charlie",1);
/*
    SELECT COMMANDS
*/
-- SELECT all from users.
SELECT * FROM users;
-- SELECT all from classifcations.
SELECT * FROM classifcations;
-- SELECT all from issues.
SELECT * FROM issues;
-- SELECT all from parents.
SELECT * FROM parent;
-- SELECT all from issues.
SELECT * FROM child;
-- SELECT all from owners.
SELECT * FROM owners;
-- SELECT all from pets.
SELECT * FROM pets;
/*
    DELETE COMMANDS
*/
-- DELETE all users.
DELETE FROM users;
-- DELETE all classifications.
DELETE FROM classifcations;
-- DELET all issues.
DELETE FROM issue;