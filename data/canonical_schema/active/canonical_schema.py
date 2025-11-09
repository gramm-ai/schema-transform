"""
Enterprise-Grade Master Canonical Schema
Version: 3.0 - Enterprise Edition
Last Updated: 2025-11-06
Approach: Universal enterprise schema with graceful degradation via mapping system

This is a comprehensive MASTER schema covering all enterprise business entities.
Designed for Contract Lifecycle Management (CLM) and enterprise operations.
Client mappings handle unavailable fields gracefully using type='unavailable'.

Ontology Alignment: FIBO (Financial Industry Business Ontology)
Coverage: Contract management, organizational hierarchy, compliance, governance
"""

# Master canonical schema - comprehensive and stable for enterprise deployments
CANONICAL_SCHEMA = {
    # ====================
    # CORE CONTRACT ENTITIES
    # ====================
    
    "contract": {
        "id": "unique identifier for the contract (FIBO: fibo:hasIdentifier)",
        "name": "contract name or title (FIBO: fibo:hasName)",
        "contract_number": "human-readable contract number (FIBO: fibo:hasContractIdentifier)",
        "customer": "legal entity that is party to the contract (FIBO: fibo:hasContractParty)",
        "customer_id": "reference to customer entity (FIBO: fibo:hasPartyIdentifier)",
        "vendor_id": "reference to vendor entity if applicable (FIBO: fibo:hasCounterpartyIdentifier)",
        "parent_contract_id": "reference to parent/master contract (FIBO: fibo:hasParentContract)",
        "total_value": "monetary value of the contract over its lifetime (FIBO: fibo:hasContractValue)",
        "annual_value": "annual recurring revenue or annual contract value (FIBO: fibo:hasAnnualValue)",
        "currency": "currency code for monetary values (FIBO: fibo:hasCurrency)",
        "status": "current lifecycle status of the contract (FIBO: fibo:hasContractStatus)",
        "contract_type": "type or category of contract (FIBO: fibo:hasContractType)",
        "business_unit": "owning business unit or department (FIBO: fibo:hasBusinessUnit)",
        "owner_id": "contract owner/manager user id (FIBO: fibo:hasResponsibleParty)",
        "start_date": "date when contract becomes effective (FIBO: fibo:hasEffectiveDate)",
        "expiry_date": "date when contract terminates (FIBO: fibo:hasTerminationDate)",
        "renewal_date": "next renewal date (FIBO: fibo:hasRenewalDate)",
        "auto_renewal": "whether contract automatically renews (FIBO: fibo:isAutomaticallyRenewable)",
        "renewal_notice_days": "days notice required before renewal (FIBO: fibo:hasNotificationPeriod)",
        "term_length": "contract term length in months (FIBO: fibo:hasContractTerm)",
        "payment_terms": "payment terms and conditions (FIBO: fibo:hasPaymentTerms)",
        "region": "geographic region or territory (FIBO: fibo:hasRegion)",
        "risk_level": "risk assessment: low, medium, high, critical (FIBO: fibo:hasRiskLevel)",
        "compliance_status": "compliance check status (FIBO: fibo:hasComplianceStatus)",
        "approval_status": "approval workflow status (FIBO: fibo:hasApprovalStatus)",
        "signed_date": "date contract was signed (FIBO: fibo:hasExecutionDate)",
        "governing_law": "governing law jurisdiction (FIBO: fibo:hasGoverningLaw)",
        "created_date": "date when contract record was created (FIBO: fibo:hasCreationDate)",
        "created_by": "user who created the contract (FIBO: fibo:hasCreator)",
        "modified_date": "date when contract was last modified (FIBO: fibo:hasModificationDate)",
        "modified_by": "user who last modified the contract (FIBO: fibo:hasModifier)",
        "archived": "whether contract is archived (FIBO: fibo:isArchived)",
        "notes": "general notes or comments (FIBO: fibo:hasNote)"
    },
    
    "contract_amendment": {
        "id": "unique amendment identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to parent contract (FIBO: fibo:hasContractIdentifier)",
        "amendment_number": "sequential amendment number (FIBO: fibo:hasAmendmentNumber)",
        "amendment_type": "type of amendment: modification, extension, termination (FIBO: fibo:hasAmendmentType)",
        "description": "description of changes (FIBO: fibo:hasDescription)",
        "effective_date": "date amendment becomes effective (FIBO: fibo:hasEffectiveDate)",
        "value_change": "change in contract value (FIBO: fibo:hasValueAdjustment)",
        "term_change": "change in contract term (FIBO: fibo:hasTermAdjustment)",
        "status": "amendment status: draft, pending, approved, executed (FIBO: fibo:hasStatus)",
        "approval_date": "date amendment was approved (FIBO: fibo:hasApprovalDate)",
        "approved_by": "user who approved amendment (FIBO: fibo:hasApprover)",
        "created_date": "date amendment was created (FIBO: fibo:hasCreationDate)",
        "created_by": "user who created amendment (FIBO: fibo:hasCreator)"
    },
    
    "service_level_agreement": {
        "id": "unique SLA identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "sla_name": "name or title of SLA (FIBO: fibo:hasName)",
        "sla_type": "type of SLA: availability, performance, support (FIBO: fibo:hasSLAType)",
        "metric_name": "name of measured metric (FIBO: fibo:hasMetricName)",
        "target_value": "target/threshold value (FIBO: fibo:hasTargetValue)",
        "measurement_unit": "unit of measurement (FIBO: fibo:hasMeasurementUnit)",
        "measurement_period": "measurement period: daily, monthly, quarterly (FIBO: fibo:hasMeasurementPeriod)",
        "penalty_amount": "penalty for SLA breach (FIBO: fibo:hasPenaltyAmount)",
        "penalty_type": "type of penalty: credit, rebate, termination right (FIBO: fibo:hasPenaltyType)",
        "status": "SLA status: active, breached, suspended (FIBO: fibo:hasStatus)",
        "effective_date": "date SLA becomes effective (FIBO: fibo:hasEffectiveDate)",
        "expiry_date": "date SLA expires (FIBO: fibo:hasExpiryDate)",
        "created_date": "date SLA was created (FIBO: fibo:hasCreationDate)"
    },
    
    "milestone": {
        "id": "unique milestone identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "milestone_name": "name or title of milestone (FIBO: fibo:hasName)",
        "description": "milestone description (FIBO: fibo:hasDescription)",
        "milestone_type": "type: deliverable, payment, approval, review (FIBO: fibo:hasMilestoneType)",
        "due_date": "milestone due date (FIBO: fibo:hasDueDate)",
        "completion_date": "actual completion date (FIBO: fibo:hasCompletionDate)",
        "status": "milestone status: pending, in_progress, completed, delayed, cancelled (FIBO: fibo:hasStatus)",
        "owner_id": "user responsible for milestone (FIBO: fibo:hasResponsibleParty)",
        "value": "monetary value associated with milestone (FIBO: fibo:hasValue)",
        "dependencies": "dependent milestone IDs (FIBO: fibo:hasDependency)",
        "completion_criteria": "criteria for completion (FIBO: fibo:hasCompletionCriteria)",
        "created_date": "date milestone was created (FIBO: fibo:hasCreationDate)"
    },
    
    "obligation": {
        "id": "unique obligation identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "obligation_name": "name or title of obligation (FIBO: fibo:hasName)",
        "description": "detailed description (FIBO: fibo:hasDescription)",
        "obligation_type": "type: payment, delivery, service, compliance (FIBO: fibo:hasObligationType)",
        "party_responsible": "party responsible: customer, vendor, both (FIBO: fibo:hasResponsibleParty)",
        "due_date": "obligation due date (FIBO: fibo:hasDueDate)",
        "completion_date": "actual completion date (FIBO: fibo:hasCompletionDate)",
        "status": "obligation status: pending, fulfilled, breached, waived (FIBO: fibo:hasStatus)",
        "frequency": "recurrence: one-time, monthly, quarterly, annual (FIBO: fibo:hasFrequency)",
        "severity": "severity if not met: low, medium, high, critical (FIBO: fibo:hasSeverity)",
        "created_date": "date obligation was created (FIBO: fibo:hasCreationDate)"
    },
    
    # ====================
    # ORGANIZATIONAL ENTITIES
    # ====================
    
    "customer": {
        "id": "unique customer identifier (FIBO: fibo:hasIdentifier)",
        "name": "customer or company name (FIBO: fibo:hasLegalName)",
        "customer_number": "human-readable customer number (FIBO: fibo:hasCustomerIdentifier)",
        "parent_customer_id": "parent company if subsidiary (FIBO: fibo:hasParentOrganization)",
        "type": "customer type or category (FIBO: fibo:hasOrganizationType)",
        "industry": "industry or business sector (FIBO: fibo:hasIndustryClassification)",
        "region": "geographic region (FIBO: fibo:hasRegion)",
        "country": "country code or name (FIBO: fibo:hasCountry)",
        "account_status": "account status: active, inactive, suspended (FIBO: fibo:hasAccountStatus)",
        "credit_rating": "customer credit rating or score (FIBO: fibo:hasCreditRating)",
        "risk_tier": "risk classification: low, medium, high (FIBO: fibo:hasRiskTier)",
        "account_manager_id": "assigned account manager (FIBO: fibo:hasAccountManager)",
        "created_date": "customer creation date (FIBO: fibo:hasCreationDate)",
        "lifetime_value": "total revenue from customer (FIBO: fibo:hasLifetimeValue)",
        "annual_revenue": "estimated annual revenue (FIBO: fibo:hasAnnualRevenue)",
        "employee_count": "number of employees (FIBO: fibo:hasEmployeeCount)",
        "contact_email": "primary contact email (FIBO: fibo:hasContactEmail)",
        "contact_phone": "primary contact phone (FIBO: fibo:hasContactPhone)",
        "address": "physical or registered address (FIBO: fibo:hasAddress)",
        "tax_id": "tax identification number (FIBO: fibo:hasTaxIdentifier)",
        "website": "company website URL (FIBO: fibo:hasWebsite)",
        "notes": "customer notes (FIBO: fibo:hasNote)"
    },
    
    "business_unit": {
        "id": "unique business unit identifier (FIBO: fibo:hasIdentifier)",
        "name": "business unit name (FIBO: fibo:hasName)",
        "code": "business unit code (FIBO: fibo:hasCode)",
        "parent_unit_id": "parent business unit (FIBO: fibo:hasParentUnit)",
        "unit_type": "type: division, department, team, cost center (FIBO: fibo:hasUnitType)",
        "manager_id": "business unit manager (FIBO: fibo:hasManager)",
        "budget": "annual budget (FIBO: fibo:hasBudget)",
        "currency": "budget currency (FIBO: fibo:hasCurrency)",
        "region": "geographic region (FIBO: fibo:hasRegion)",
        "country": "country (FIBO: fibo:hasCountry)",
        "status": "unit status: active, inactive, merged (FIBO: fibo:hasStatus)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)",
        "closed_date": "closure date if applicable (FIBO: fibo:hasClosureDate)"
    },
    
    "user": {
        "id": "unique user identifier (FIBO: fibo:hasIdentifier)",
        "username": "login username (FIBO: fibo:hasUsername)",
        "email": "user email address (FIBO: fibo:hasEmail)",
        "first_name": "first name (FIBO: fibo:hasGivenName)",
        "last_name": "last name (FIBO: fibo:hasFamilyName)",
        "full_name": "full display name (FIBO: fibo:hasName)",
        "job_title": "job title or position (FIBO: fibo:hasJobTitle)",
        "department": "department name (FIBO: fibo:hasDepartment)",
        "business_unit_id": "assigned business unit (FIBO: fibo:hasBusinessUnitIdentifier)",
        "manager_id": "reporting manager (FIBO: fibo:hasManagerIdentifier)",
        "phone": "contact phone number (FIBO: fibo:hasPhone)",
        "status": "user status: active, inactive, suspended (FIBO: fibo:hasStatus)",
        "role": "primary role (FIBO: fibo:hasRole)",
        "hire_date": "employment start date (FIBO: fibo:hasHireDate)",
        "termination_date": "employment end date (FIBO: fibo:hasTerminationDate)",
        "created_date": "account creation date (FIBO: fibo:hasCreationDate)",
        "last_login": "last login timestamp (FIBO: fibo:hasLastLoginDate)"
    },
    
    "contact": {
        "id": "unique contact identifier (FIBO: fibo:hasIdentifier)",
        "customer_id": "associated customer (FIBO: fibo:hasCustomerIdentifier)",
        "vendor_id": "associated vendor if applicable (FIBO: fibo:hasVendorIdentifier)",
        "first_name": "first name (FIBO: fibo:hasGivenName)",
        "last_name": "last name (FIBO: fibo:hasFamilyName)",
        "full_name": "full name (FIBO: fibo:hasName)",
        "email": "email address (FIBO: fibo:hasEmail)",
        "phone": "phone number (FIBO: fibo:hasPhone)",
        "mobile": "mobile number (FIBO: fibo:hasMobile)",
        "job_title": "job title (FIBO: fibo:hasJobTitle)",
        "department": "department (FIBO: fibo:hasDepartment)",
        "contact_type": "type: primary, billing, technical, executive (FIBO: fibo:hasContactType)",
        "is_primary": "whether primary contact (FIBO: fibo:isPrimaryContact)",
        "is_decision_maker": "whether decision maker (FIBO: fibo:isDecisionMaker)",
        "status": "contact status: active, inactive (FIBO: fibo:hasStatus)",
        "created_date": "date contact was added (FIBO: fibo:hasCreationDate)"
    },
    
    # ====================
    # FINANCIAL ENTITIES
    # ====================
    
    "invoice": {
        "id": "unique invoice identifier (FIBO: fibo:hasIdentifier)",
        "invoice_number": "human-readable invoice number (FIBO: fibo:hasInvoiceNumber)",
        "customer_id": "reference to customer (FIBO: fibo:hasPartyIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "business_unit_id": "invoicing business unit (FIBO: fibo:hasBusinessUnitIdentifier)",
        "amount": "invoice total amount (FIBO: fibo:hasInvoiceAmount)",
        "currency": "invoice currency code (FIBO: fibo:hasCurrency)",
        "tax_amount": "tax amount (FIBO: fibo:hasTaxAmount)",
        "subtotal": "amount before tax (FIBO: fibo:hasSubtotalAmount)",
        "discount_amount": "discount applied (FIBO: fibo:hasDiscountAmount)",
        "status": "invoice status: draft, sent, paid, overdue, cancelled (FIBO: fibo:hasInvoiceStatus)",
        "invoice_type": "type: standard, credit_note, debit_note, proforma (FIBO: fibo:hasInvoiceType)",
        "billing_period_start": "billing period start date (FIBO: fibo:hasPeriodStartDate)",
        "billing_period_end": "billing period end date (FIBO: fibo:hasPeriodEndDate)",
        "issue_date": "invoice issue date (FIBO: fibo:hasIssueDate)",
        "due_date": "payment due date (FIBO: fibo:hasDueDate)",
        "paid_date": "actual payment date (FIBO: fibo:hasPaymentDate)",
        "payment_method": "method of payment (FIBO: fibo:hasPaymentMethod)",
        "payment_terms": "payment terms (FIBO: fibo:hasPaymentTerms)",
        "line_items": "invoice line item details (FIBO: fibo:hasLineItem)",
        "notes": "additional notes or comments (FIBO: fibo:hasNote)",
        "created_date": "date invoice was created (FIBO: fibo:hasCreationDate)",
        "created_by": "user who created invoice (FIBO: fibo:hasCreator)"
    },
    
    "payment": {
        "id": "unique payment identifier (FIBO: fibo:hasIdentifier)",
        "payment_number": "human-readable payment reference (FIBO: fibo:hasPaymentReference)",
        "invoice_id": "reference to invoice (FIBO: fibo:hasInvoiceIdentifier)",
        "contract_id": "reference to contract if applicable (FIBO: fibo:hasContractIdentifier)",
        "customer_id": "reference to customer (FIBO: fibo:hasPartyIdentifier)",
        "amount": "payment amount (FIBO: fibo:hasPaymentAmount)",
        "currency": "payment currency code (FIBO: fibo:hasCurrency)",
        "payment_date": "date payment was made (FIBO: fibo:hasPaymentDate)",
        "payment_method": "payment method: wire, credit card, check, ACH (FIBO: fibo:hasPaymentMethod)",
        "status": "payment status: pending, completed, failed, refunded (FIBO: fibo:hasPaymentStatus)",
        "transaction_id": "external transaction identifier (FIBO: fibo:hasTransactionIdentifier)",
        "reference_number": "payment reference number (FIBO: fibo:hasReferenceNumber)",
        "bank_account": "bank account used (FIBO: fibo:hasBankAccount)",
        "notes": "payment notes (FIBO: fibo:hasNote)",
        "processed_by": "user who processed payment (FIBO: fibo:hasProcessor)",
        "created_date": "date payment record was created (FIBO: fibo:hasCreationDate)"
    },
    
    "revenue_recognition": {
        "id": "unique revenue recognition identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "invoice_id": "reference to invoice if applicable (FIBO: fibo:hasInvoiceIdentifier)",
        "recognition_period": "accounting period (FIBO: fibo:hasAccountingPeriod)",
        "amount": "recognized revenue amount (FIBO: fibo:hasRevenueAmount)",
        "currency": "currency code (FIBO: fibo:hasCurrency)",
        "recognition_date": "date revenue recognized (FIBO: fibo:hasRecognitionDate)",
        "recognition_method": "method: straight-line, milestone, percentage-of-completion (FIBO: fibo:hasRecognitionMethod)",
        "deferred_amount": "amount deferred (FIBO: fibo:hasDeferredAmount)",
        "business_unit_id": "business unit (FIBO: fibo:hasBusinessUnitIdentifier)",
        "status": "status: pending, recognized, reversed (FIBO: fibo:hasStatus)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)"
    },
    
    # ====================
    # PRODUCT & CATALOG ENTITIES
    # ====================
    
    "product": {
        "id": "unique product identifier (FIBO: fibo:hasIdentifier)",
        "name": "product name (FIBO: fibo:hasProductName)",
        "sku": "stock keeping unit (FIBO: fibo:hasSKU)",
        "product_code": "internal product code (FIBO: fibo:hasProductCode)",
        "category": "product category (FIBO: fibo:hasProductCategory)",
        "subcategory": "product subcategory (FIBO: fibo:hasProductSubcategory)",
        "product_family": "product family or line (FIBO: fibo:hasProductFamily)",
        "price": "standard unit price (FIBO: fibo:hasPrice)",
        "currency": "price currency (FIBO: fibo:hasCurrency)",
        "cost": "cost of goods (FIBO: fibo:hasCostOfGoods)",
        "status": "product status: active, discontinued, pending (FIBO: fibo:hasProductStatus)",
        "description": "product description (FIBO: fibo:hasDescription)",
        "unit_of_measure": "unit of measure (e.g., each, license, kg) (FIBO: fibo:hasUnitOfMeasure)",
        "is_subscription": "whether subscription-based (FIBO: fibo:isSubscriptionBased)",
        "subscription_term": "subscription term if applicable (FIBO: fibo:hasSubscriptionTerm)",
        "supplier_id": "reference to supplier (FIBO: fibo:hasSupplierIdentifier)",
        "created_date": "date product was created (FIBO: fibo:hasCreationDate)",
        "modified_date": "date product was last modified (FIBO: fibo:hasModificationDate)"
    },
    
    "license": {
        "id": "unique license identifier (FIBO: fibo:hasIdentifier)",
        "license_key": "license key or token (FIBO: fibo:hasLicenseKey)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "customer_id": "reference to customer (FIBO: fibo:hasCustomerIdentifier)",
        "product_id": "reference to product (FIBO: fibo:hasProductIdentifier)",
        "license_type": "type: perpetual, subscription, trial, evaluation (FIBO: fibo:hasLicenseType)",
        "quantity": "number of licenses (FIBO: fibo:hasQuantity)",
        "unit_type": "unit: user, device, server, concurrent (FIBO: fibo:hasUnitType)",
        "status": "license status: active, expired, suspended, revoked (FIBO: fibo:hasStatus)",
        "issue_date": "date license was issued (FIBO: fibo:hasIssueDate)",
        "activation_date": "date license was activated (FIBO: fibo:hasActivationDate)",
        "expiry_date": "license expiration date (FIBO: fibo:hasExpiryDate)",
        "renewal_date": "renewal date (FIBO: fibo:hasRenewalDate)",
        "auto_renewal": "whether automatically renews (FIBO: fibo:isAutoRenewable)",
        "assigned_users": "users assigned to license (FIBO: fibo:hasAssignedUsers)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)"
    },
    
    # ====================
    # PROCUREMENT ENTITIES
    # ====================
    
    "order": {
        "id": "unique order identifier (FIBO: fibo:hasIdentifier)",
        "order_number": "human-readable order number (FIBO: fibo:hasOrderNumber)",
        "customer_id": "reference to customer (FIBO: fibo:hasPartyIdentifier)",
        "contract_id": "reference to contract if applicable (FIBO: fibo:hasContractIdentifier)",
        "business_unit_id": "ordering business unit (FIBO: fibo:hasBusinessUnitIdentifier)",
        "total_amount": "order total amount (FIBO: fibo:hasOrderAmount)",
        "currency": "order currency code (FIBO: fibo:hasCurrency)",
        "tax_amount": "tax amount (FIBO: fibo:hasTaxAmount)",
        "subtotal": "amount before tax (FIBO: fibo:hasSubtotalAmount)",
        "discount_amount": "discount applied (FIBO: fibo:hasDiscountAmount)",
        "status": "order status: pending, confirmed, shipped, delivered, cancelled (FIBO: fibo:hasOrderStatus)",
        "order_type": "type: new, renewal, upgrade, amendment (FIBO: fibo:hasOrderType)",
        "order_date": "order creation date (FIBO: fibo:hasOrderDate)",
        "ship_date": "shipment date (FIBO: fibo:hasShipmentDate)",
        "delivery_date": "actual delivery date (FIBO: fibo:hasDeliveryDate)",
        "expected_delivery": "expected delivery date (FIBO: fibo:hasExpectedDeliveryDate)",
        "shipping_address": "shipping address (FIBO: fibo:hasShippingAddress)",
        "billing_address": "billing address (FIBO: fibo:hasBillingAddress)",
        "line_items": "order line items (FIBO: fibo:hasLineItem)",
        "notes": "order notes or special instructions (FIBO: fibo:hasNote)",
        "created_date": "date order record was created (FIBO: fibo:hasCreationDate)",
        "created_by": "user who created order (FIBO: fibo:hasCreator)"
    },
    
    "vendor": {
        "id": "unique vendor identifier (FIBO: fibo:hasIdentifier)",
        "name": "vendor or supplier name (FIBO: fibo:hasLegalName)",
        "vendor_number": "human-readable vendor number (FIBO: fibo:hasVendorIdentifier)",
        "parent_vendor_id": "parent company if subsidiary (FIBO: fibo:hasParentOrganization)",
        "type": "vendor type or category (FIBO: fibo:hasOrganizationType)",
        "category": "vendor category or classification (FIBO: fibo:hasVendorCategory)",
        "status": "vendor status: active, inactive, suspended, blacklisted (FIBO: fibo:hasVendorStatus)",
        "risk_rating": "vendor risk rating: low, medium, high, critical (FIBO: fibo:hasRiskRating)",
        "performance_score": "vendor performance score (FIBO: fibo:hasPerformanceScore)",
        "country": "vendor country (FIBO: fibo:hasCountry)",
        "region": "vendor region (FIBO: fibo:hasRegion)",
        "payment_terms": "standard payment terms (FIBO: fibo:hasPaymentTerms)",
        "contact_email": "primary contact email (FIBO: fibo:hasContactEmail)",
        "contact_phone": "primary contact phone (FIBO: fibo:hasContactPhone)",
        "address": "vendor address (FIBO: fibo:hasAddress)",
        "tax_id": "vendor tax identification number (FIBO: fibo:hasTaxIdentifier)",
        "website": "vendor website (FIBO: fibo:hasWebsite)",
        "created_date": "vendor creation date (FIBO: fibo:hasCreationDate)",
        "approved_date": "vendor approval date (FIBO: fibo:hasApprovalDate)",
        "approved_by": "user who approved vendor (FIBO: fibo:hasApprover)"
    },
    
    # ====================
    # GOVERNANCE & COMPLIANCE
    # ====================
    
    "agreement": {
        "id": "unique agreement identifier (FIBO: fibo:hasIdentifier)",
        "agreement_number": "human-readable agreement number (FIBO: fibo:hasAgreementNumber)",
        "matter_number": "legal matter number (FIBO: fibo:hasMatterNumber)",
        "party_id": "reference to party (customer/client) (FIBO: fibo:hasPartyIdentifier)",
        "agreement_type": "type of agreement (FIBO: fibo:hasAgreementType)",
        "total_fees": "total fees or value (FIBO: fibo:hasAgreementValue)",
        "retainer_amount": "retainer or advance amount (FIBO: fibo:hasRetainerAmount)",
        "currency": "currency code (FIBO: fibo:hasCurrency)",
        "status": "agreement status (FIBO: fibo:hasAgreementStatus)",
        "effective_date": "date agreement becomes effective (FIBO: fibo:hasEffectiveDate)",
        "termination_date": "date agreement terminates (FIBO: fibo:hasTerminationDate)",
        "jurisdiction": "legal jurisdiction (FIBO: fibo:hasJurisdiction)",
        "governing_law": "governing law (FIBO: fibo:hasGoverningLaw)",
        "confidentiality_level": "confidentiality classification (FIBO: fibo:hasConfidentialityLevel)",
        "created_date": "date agreement was created (FIBO: fibo:hasCreationDate)"
    },
    
    "document": {
        "id": "unique document identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "document_name": "document name or title (FIBO: fibo:hasName)",
        "document_type": "type: contract, amendment, addendum, SOW, NDA, PO (FIBO: fibo:hasDocumentType)",
        "version": "document version number (FIBO: fibo:hasVersion)",
        "status": "document status: draft, review, approved, executed, archived (FIBO: fibo:hasStatus)",
        "file_path": "storage file path or URL (FIBO: fibo:hasFilePath)",
        "file_size": "file size in bytes (FIBO: fibo:hasFileSize)",
        "file_format": "file format: PDF, DOCX, etc. (FIBO: fibo:hasFileFormat)",
        "signed": "whether document is signed (FIBO: fibo:isSigned)",
        "signature_date": "date document was signed (FIBO: fibo:hasSignatureDate)",
        "effective_date": "document effective date (FIBO: fibo:hasEffectiveDate)",
        "expiry_date": "document expiry date (FIBO: fibo:hasExpiryDate)",
        "owner_id": "document owner (FIBO: fibo:hasOwner)",
        "created_date": "upload date (FIBO: fibo:hasCreationDate)",
        "created_by": "user who uploaded (FIBO: fibo:hasCreator)",
        "modified_date": "last modification date (FIBO: fibo:hasModificationDate)",
        "modified_by": "last user who modified (FIBO: fibo:hasModifier)"
    },
    
    "approval": {
        "id": "unique approval identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "approval_type": "type: contract, amendment, invoice, payment (FIBO: fibo:hasApprovalType)",
        "approval_stage": "workflow stage (FIBO: fibo:hasApprovalStage)",
        "status": "approval status: pending, approved, rejected, cancelled (FIBO: fibo:hasStatus)",
        "approver_id": "user who must approve (FIBO: fibo:hasApproverIdentifier)",
        "approver_role": "role required: manager, legal, finance, executive (FIBO: fibo:hasApproverRole)",
        "submission_date": "date submitted for approval (FIBO: fibo:hasSubmissionDate)",
        "decision_date": "date decision was made (FIBO: fibo:hasDecisionDate)",
        "comments": "approver comments (FIBO: fibo:hasComment)",
        "delegated_to": "user approval was delegated to (FIBO: fibo:hasDelegateIdentifier)",
        "sequence": "approval sequence number (FIBO: fibo:hasSequence)",
        "is_parallel": "whether parallel approval (FIBO: fibo:isParallelApproval)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)"
    },
    
    "audit_log": {
        "id": "unique audit log identifier (FIBO: fibo:hasIdentifier)",
        "entity_type": "type of entity: contract, invoice, user, etc. (FIBO: fibo:hasEntityType)",
        "entity_id": "identifier of the entity (FIBO: fibo:hasEntityIdentifier)",
        "action": "action performed: create, update, delete, approve, etc. (FIBO: fibo:hasAction)",
        "user_id": "user who performed action (FIBO: fibo:hasUserIdentifier)",
        "timestamp": "timestamp of action (FIBO: fibo:hasTimestamp)",
        "ip_address": "IP address of user (FIBO: fibo:hasIPAddress)",
        "old_value": "previous value (FIBO: fibo:hasOldValue)",
        "new_value": "new value (FIBO: fibo:hasNewValue)",
        "field_changed": "field that was changed (FIBO: fibo:hasFieldName)",
        "description": "description of change (FIBO: fibo:hasDescription)",
        "session_id": "user session identifier (FIBO: fibo:hasSessionIdentifier)"
    },
    
    "compliance_requirement": {
        "id": "unique requirement identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "requirement_name": "name of requirement (FIBO: fibo:hasName)",
        "requirement_type": "type: regulatory, contractual, internal (FIBO: fibo:hasRequirementType)",
        "regulation": "regulation name: GDPR, SOX, HIPAA, etc. (FIBO: fibo:hasRegulation)",
        "description": "detailed description (FIBO: fibo:hasDescription)",
        "status": "compliance status: compliant, non_compliant, pending, waived (FIBO: fibo:hasComplianceStatus)",
        "due_date": "compliance due date (FIBO: fibo:hasDueDate)",
        "certification_date": "date of certification (FIBO: fibo:hasCertificationDate)",
        "certification_expiry": "certification expiry date (FIBO: fibo:hasExpiryDate)",
        "responsible_party": "party responsible (FIBO: fibo:hasResponsibleParty)",
        "severity": "severity: low, medium, high, critical (FIBO: fibo:hasSeverity)",
        "evidence_required": "whether evidence required (FIBO: fibo:requiresEvidence)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)"
    },
    
    "risk_assessment": {
        "id": "unique risk assessment identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "risk_type": "type: financial, operational, legal, reputational (FIBO: fibo:hasRiskType)",
        "risk_description": "description of risk (FIBO: fibo:hasDescription)",
        "probability": "probability: low, medium, high (FIBO: fibo:hasProbability)",
        "impact": "impact: low, medium, high, critical (FIBO: fibo:hasImpact)",
        "risk_score": "calculated risk score (FIBO: fibo:hasRiskScore)",
        "risk_level": "overall level: low, medium, high, critical (FIBO: fibo:hasRiskLevel)",
        "mitigation_strategy": "mitigation approach (FIBO: fibo:hasMitigationStrategy)",
        "mitigation_status": "status: identified, planned, implemented, monitored (FIBO: fibo:hasStatus)",
        "owner_id": "risk owner (FIBO: fibo:hasOwnerIdentifier)",
        "assessment_date": "date of assessment (FIBO: fibo:hasAssessmentDate)",
        "review_date": "next review date (FIBO: fibo:hasReviewDate)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)",
        "created_by": "assessor (FIBO: fibo:hasCreator)"
    },
    
    # ====================
    # OPPORTUNITY & SALES
    # ====================
    
    "opportunity": {
        "id": "unique opportunity identifier (FIBO: fibo:hasIdentifier)",
        "opportunity_name": "opportunity name (FIBO: fibo:hasName)",
        "customer_id": "reference to customer (FIBO: fibo:hasCustomerIdentifier)",
        "contract_id": "reference to contract if converted (FIBO: fibo:hasContractIdentifier)",
        "opportunity_type": "type: new_business, renewal, upsell, cross_sell (FIBO: fibo:hasOpportunityType)",
        "stage": "sales stage: lead, qualified, proposal, negotiation, closed_won, closed_lost (FIBO: fibo:hasStage)",
        "probability": "win probability percentage (FIBO: fibo:hasProbability)",
        "estimated_value": "estimated contract value (FIBO: fibo:hasEstimatedValue)",
        "currency": "currency code (FIBO: fibo:hasCurrency)",
        "expected_close_date": "expected close date (FIBO: fibo:hasExpectedCloseDate)",
        "actual_close_date": "actual close date (FIBO: fibo:hasActualCloseDate)",
        "owner_id": "sales owner (FIBO: fibo:hasOwnerIdentifier)",
        "source": "lead source (FIBO: fibo:hasSource)",
        "status": "status: open, won, lost, abandoned (FIBO: fibo:hasStatus)",
        "loss_reason": "reason for loss if applicable (FIBO: fibo:hasLossReason)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)",
        "created_by": "creator (FIBO: fibo:hasCreator)"
    },
    
    "renewal": {
        "id": "unique renewal identifier (FIBO: fibo:hasIdentifier)",
        "contract_id": "reference to original contract (FIBO: fibo:hasContractIdentifier)",
        "renewal_contract_id": "reference to renewed contract (FIBO: fibo:hasRenewalContractIdentifier)",
        "renewal_type": "type: auto, negotiated, amended (FIBO: fibo:hasRenewalType)",
        "renewal_date": "renewal effective date (FIBO: fibo:hasRenewalDate)",
        "notice_date": "date notice was given/due (FIBO: fibo:hasNoticeDate)",
        "status": "renewal status: upcoming, in_progress, completed, declined (FIBO: fibo:hasStatus)",
        "original_value": "original contract value (FIBO: fibo:hasOriginalValue)",
        "renewal_value": "renewal contract value (FIBO: fibo:hasRenewalValue)",
        "value_change_pct": "percentage change in value (FIBO: fibo:hasValueChangePercentage)",
        "term_length": "renewal term length (FIBO: fibo:hasTermLength)",
        "owner_id": "renewal owner (FIBO: fibo:hasOwnerIdentifier)",
        "decision_date": "date decision was made (FIBO: fibo:hasDecisionDate)",
        "decline_reason": "reason for declining renewal (FIBO: fibo:hasDeclineReason)",
        "created_date": "creation date (FIBO: fibo:hasCreationDate)"
    }
}
