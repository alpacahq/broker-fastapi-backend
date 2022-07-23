from faker import Faker

fake = Faker()
print(fake.name())
# 'Lucy Cechtelar'

print(fake.street_address())



# Contact
contact_data = Contact(
            email_address=fake.email(),
            phone_number=fake.phone_number(),
            street_address=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            postal_code=fake.postcode(),
            country=fake.country()
            )
# Identity
identity_data = Identity(
        given_name=fake.first_name(),
        middle_name=fake.middle_name(),
        family_name=fake.last_name(),
        date_of_birth=fake.date_of_birth(),
        tax_id=fake.ssn(),
        tax_id_type=TaxIdType.USA_SSN,
        country_of_citizenship="USA",
        country_of_birth="USA",
        country_of_tax_residence="USA",
        funding_source=[FundingSource.EMPLOYMENT_INCOME]
        )