**Overview**

The Vendor Management System (VMS) is a web-based application designed to streamline and automate the process of managing vendors and their contracts. The system provides a centralized platform for organizations to manage their vendor relationships, ensuring compliance with company policies and regulations, and facilitating efficient communication between vendors and internal teams.


**USER CATEGORY PAYLOAD**:

    SELLER ONBOARDING 
    Payload:
        first_name
        last_name
        mobile
        password
        is_accept_terms_and_condition (True/False)
        

    BUYER ONBOARDING
    Payload:
        first_name
        last_name
        email
        phone
        password
        type -> this can either be individual or business
        business_name -> to be added to payload if ``type`` is business
