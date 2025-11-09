"""
Schema repository and definitions
Centralizes all customer schema metadata
"""
import os
from typing import Dict, Any, List
from functools import lru_cache
from pathlib import Path
from app.core.exceptions import CustomerNotFoundError

# Master Canonical Schema - Comprehensive and Stable
# This schema covers all common business entities and should NOT be regenerated for new clients.
# Client-specific variations are handled through mapping files with type='unavailable' for missing fields.
CANONICAL_SCHEMA = {
    "contract": {
        "id": "unique identifier for the contract (FIBO: fibo:hasIdentifier)",
        "name": "contract name or title (FIBO: fibo:hasName)",
        "contract_number": "human-readable contract number (FIBO: fibo:hasContractIdentifier)",
        "customer": "legal entity that is party to the contract (FIBO: fibo:hasContractParty)",
        "customer_id": "reference to customer entity (FIBO: fibo:hasPartyIdentifier)",
        "total_value": "monetary value of the contract over its lifetime (FIBO: fibo:hasContractValue)",
        "annual_value": "annual recurring revenue or annual contract value (FIBO: fibo:hasAnnualValue)",
        "currency": "currency code for monetary values (FIBO: fibo:hasCurrency)",
        "status": "current lifecycle status of the contract (FIBO: fibo:hasContractStatus)",
        "contract_type": "type or category of contract (FIBO: fibo:hasContractType)",
        "start_date": "date when contract becomes effective (FIBO: fibo:hasEffectiveDate)",
        "expiry_date": "date when contract terminates (FIBO: fibo:hasTerminationDate)",
        "renewal_date": "next renewal date (FIBO: fibo:hasRenewalDate)",
        "auto_renewal": "whether contract automatically renews (FIBO: fibo:isAutomaticallyRenewable)",
        "term_length": "contract term length in months (FIBO: fibo:hasContractTerm)",
        "payment_terms": "payment terms and conditions (FIBO: fibo:hasPaymentTerms)",
        "region": "geographic region or territory (FIBO: fibo:hasRegion)",
        "created_date": "date when contract record was created (FIBO: fibo:hasCreationDate)",
        "modified_date": "date when contract was last modified (FIBO: fibo:hasModificationDate)"
    },
    "customer": {
        "id": "unique customer identifier (FIBO: fibo:hasIdentifier)",
        "name": "customer or company name (FIBO: fibo:hasLegalName)",
        "customer_number": "human-readable customer number (FIBO: fibo:hasCustomerIdentifier)",
        "type": "customer type or category (FIBO: fibo:hasOrganizationType)",
        "industry": "industry or business sector (FIBO: fibo:hasIndustryClassification)",
        "region": "geographic region (FIBO: fibo:hasRegion)",
        "country": "country code or name (FIBO: fibo:hasCountry)",
        "account_status": "account status: active, inactive, suspended (FIBO: fibo:hasAccountStatus)",
        "credit_rating": "customer credit rating or score (FIBO: fibo:hasCreditRating)",
        "created_date": "customer creation date (FIBO: fibo:hasCreationDate)",
        "lifetime_value": "total revenue from customer (FIBO: fibo:hasLifetimeValue)",
        "contact_email": "primary contact email (FIBO: fibo:hasContactEmail)",
        "contact_phone": "primary contact phone (FIBO: fibo:hasContactPhone)",
        "address": "physical or registered address (FIBO: fibo:hasAddress)",
        "tax_id": "tax identification number (FIBO: fibo:hasTaxIdentifier)"
    },
    "invoice": {
        "id": "unique invoice identifier (FIBO: fibo:hasIdentifier)",
        "invoice_number": "human-readable invoice number (FIBO: fibo:hasInvoiceNumber)",
        "customer_id": "reference to customer (FIBO: fibo:hasPartyIdentifier)",
        "contract_id": "reference to contract (FIBO: fibo:hasContractIdentifier)",
        "amount": "invoice total amount (FIBO: fibo:hasInvoiceAmount)",
        "currency": "invoice currency code (FIBO: fibo:hasCurrency)",
        "tax_amount": "tax amount (FIBO: fibo:hasTaxAmount)",
        "subtotal": "amount before tax (FIBO: fibo:hasSubtotalAmount)",
        "status": "invoice status: draft, sent, paid, overdue, cancelled (FIBO: fibo:hasInvoiceStatus)",
        "issue_date": "invoice issue date (FIBO: fibo:hasIssueDate)",
        "due_date": "payment due date (FIBO: fibo:hasDueDate)",
        "paid_date": "actual payment date (FIBO: fibo:hasPaymentDate)",
        "payment_method": "method of payment (FIBO: fibo:hasPaymentMethod)",
        "line_items": "invoice line item details (FIBO: fibo:hasLineItem)",
        "notes": "additional notes or comments (FIBO: fibo:hasNote)",
        "created_date": "date invoice was created (FIBO: fibo:hasCreationDate)"
    },
    "product": {
        "id": "unique product identifier (FIBO: fibo:hasIdentifier)",
        "name": "product name (FIBO: fibo:hasProductName)",
        "sku": "stock keeping unit (FIBO: fibo:hasSKU)",
        "product_code": "internal product code (FIBO: fibo:hasProductCode)",
        "category": "product category (FIBO: fibo:hasProductCategory)",
        "subcategory": "product subcategory (FIBO: fibo:hasProductSubcategory)",
        "price": "standard unit price (FIBO: fibo:hasPrice)",
        "currency": "price currency (FIBO: fibo:hasCurrency)",
        "cost": "cost of goods (FIBO: fibo:hasCostOfGoods)",
        "status": "product status: active, discontinued, pending (FIBO: fibo:hasProductStatus)",
        "description": "product description (FIBO: fibo:hasDescription)",
        "unit_of_measure": "unit of measure (e.g., each, license, kg) (FIBO: fibo:hasUnitOfMeasure)",
        "supplier_id": "reference to supplier (FIBO: fibo:hasSupplierIdentifier)",
        "created_date": "date product was created (FIBO: fibo:hasCreationDate)",
        "modified_date": "date product was last modified (FIBO: fibo:hasModificationDate)"
    },
    "order": {
        "id": "unique order identifier (FIBO: fibo:hasIdentifier)",
        "order_number": "human-readable order number (FIBO: fibo:hasOrderNumber)",
        "customer_id": "reference to customer (FIBO: fibo:hasPartyIdentifier)",
        "contract_id": "reference to contract if applicable (FIBO: fibo:hasContractIdentifier)",
        "total_amount": "order total amount (FIBO: fibo:hasOrderAmount)",
        "currency": "order currency code (FIBO: fibo:hasCurrency)",
        "tax_amount": "tax amount (FIBO: fibo:hasTaxAmount)",
        "subtotal": "amount before tax (FIBO: fibo:hasSubtotalAmount)",
        "status": "order status: pending, confirmed, shipped, delivered, cancelled (FIBO: fibo:hasOrderStatus)",
        "order_date": "order creation date (FIBO: fibo:hasOrderDate)",
        "ship_date": "shipment date (FIBO: fibo:hasShipmentDate)",
        "delivery_date": "actual delivery date (FIBO: fibo:hasDeliveryDate)",
        "expected_delivery": "expected delivery date (FIBO: fibo:hasExpectedDeliveryDate)",
        "shipping_address": "shipping address (FIBO: fibo:hasShippingAddress)",
        "billing_address": "billing address (FIBO: fibo:hasBillingAddress)",
        "line_items": "order line items (FIBO: fibo:hasLineItem)",
        "notes": "order notes or special instructions (FIBO: fibo:hasNote)",
        "created_date": "date order record was created (FIBO: fibo:hasCreationDate)"
    },
    "payment": {
        "id": "unique payment identifier (FIBO: fibo:hasIdentifier)",
        "payment_number": "human-readable payment reference (FIBO: fibo:hasPaymentReference)",
        "invoice_id": "reference to invoice (FIBO: fibo:hasInvoiceIdentifier)",
        "customer_id": "reference to customer (FIBO: fibo:hasPartyIdentifier)",
        "amount": "payment amount (FIBO: fibo:hasPaymentAmount)",
        "currency": "payment currency code (FIBO: fibo:hasCurrency)",
        "payment_date": "date payment was made (FIBO: fibo:hasPaymentDate)",
        "payment_method": "payment method: wire, credit card, check, ACH (FIBO: fibo:hasPaymentMethod)",
        "status": "payment status: pending, completed, failed, refunded (FIBO: fibo:hasPaymentStatus)",
        "transaction_id": "external transaction identifier (FIBO: fibo:hasTransactionIdentifier)",
        "notes": "payment notes (FIBO: fibo:hasNote)",
        "created_date": "date payment record was created (FIBO: fibo:hasCreationDate)"
    },
    "vendor": {
        "id": "unique vendor identifier (FIBO: fibo:hasIdentifier)",
        "name": "vendor or supplier name (FIBO: fibo:hasLegalName)",
        "vendor_number": "human-readable vendor number (FIBO: fibo:hasVendorIdentifier)",
        "type": "vendor type or category (FIBO: fibo:hasOrganizationType)",
        "category": "vendor category or classification (FIBO: fibo:hasVendorCategory)",
        "status": "vendor status: active, inactive, suspended (FIBO: fibo:hasVendorStatus)",
        "country": "vendor country (FIBO: fibo:hasCountry)",
        "region": "vendor region (FIBO: fibo:hasRegion)",
        "payment_terms": "standard payment terms (FIBO: fibo:hasPaymentTerms)",
        "contact_email": "primary contact email (FIBO: fibo:hasContactEmail)",
        "contact_phone": "primary contact phone (FIBO: fibo:hasContactPhone)",
        "tax_id": "vendor tax identification number (FIBO: fibo:hasTaxIdentifier)",
        "created_date": "vendor creation date (FIBO: fibo:hasCreationDate)"
    },
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
        "created_date": "date agreement was created (FIBO: fibo:hasCreationDate)"
    }
}


# Client schema definitions
# Each client is a tenant with their own customized database schema
CLIENT_SCHEMAS = {
    "client_a": {
        "connection": {
            "type": "sqlite",
            "database": "data/databases/client_a.db"
        },
        "tables": {
            "contracts": {
                "columns": {
                    "contract_id": "INTEGER PRIMARY KEY",
                    "contract_number": "VARCHAR(50)",
                    "customer_name": "VARCHAR(200)",
                    "contract_value": "DECIMAL(15,2)",  # Full lifetime value
                    "annual_value": "DECIMAL(15,2)",
                    "term_years": "INTEGER",
                    "status": "VARCHAR(50)",
                    "start_date": "DATE",
                    "expiry_date": "DATE",
                    "renewal_date": "DATE",
                    "auto_renew": "BOOLEAN",
                    "region": "VARCHAR(50)"
                },
                "semantic_context": "contract_value represents total lifetime value. Single denormalized table."
            }
        },
        "semantic_context": "E-commerce company with single-table structure. contract_value is lifetime value, not annual."
    },
    "client_b": {
        "connection": {
            "type": "sqlite",
            "database": "data/databases/client_b.db"
        },
        "tables": {
            "contract_headers": {
                "columns": {
                    "id": "INTEGER PRIMARY KEY",
                    "contract_number": "VARCHAR(50)",
                    "account_id": "INTEGER",
                    "created_date": "TIMESTAMP",
                    "status": "VARCHAR(50)"
                }
            },
            "contract_accounts": {
                "columns": {
                    "account_id": "INTEGER PRIMARY KEY",
                    "company_name": "VARCHAR(200)",
                    "industry": "VARCHAR(100)",
                    "region": "VARCHAR(50)"
                }
            },
            "contract_financial_terms": {
                "columns": {
                    "term_id": "INTEGER PRIMARY KEY",
                    "contract_id": "INTEGER",
                    "annual_recurring_revenue": "DECIMAL(15,2)",  # ARR
                    "term_months": "INTEGER",
                    "payment_frequency": "VARCHAR(50)"
                }
            },
            "contract_renewal_history": {
                "columns": {
                    "id": "INTEGER PRIMARY KEY",
                    "contract_id": "INTEGER",
                    "renewal_date": "DATE",
                    "status": "VARCHAR(50)"
                }
            }
        },
        "semantic_context": "Enterprise SaaS with normalized tables. Requires JOINs. annual_recurring_revenue (ARR) is yearly, not total. Must calculate total as ARR * (term_months / 12)."
    },
    "client_c": {
        "connection": {
            "type": "sqlite",
            "database": "data/databases/client_c.db"
        },
        "tables": {
            "agreements": {
                "columns": {
                    "agreement_id": "INTEGER PRIMARY KEY",
                    "matter_number": "VARCHAR(50)",
                    "client_id": "INTEGER",
                    "agreement_type": "VARCHAR(100)",
                    "total_fees": "DECIMAL(15,2)",
                    "retainer_amount": "DECIMAL(15,2)",
                    "effective_date": "DATE",
                    "termination_date": "DATE",
                    "status": "VARCHAR(50)"
                }
            },
            "clients": {
                "columns": {
                    "client_id": "INTEGER PRIMARY KEY",
                    "client_name": "VARCHAR(200)",
                    "client_type": "VARCHAR(50)",
                    "jurisdiction": "VARCHAR(100)"
                }
            },
            "billing_schedules": {
                "columns": {
                    "schedule_id": "INTEGER PRIMARY KEY",
                    "agreement_id": "INTEGER",
                    "billing_date": "DATE",
                    "amount_due": "DECIMAL(15,2)",
                    "amount_paid": "DECIMAL(15,2)",
                    "payment_status": "VARCHAR(50)"
                }
            }
        },
        "semantic_context": "Legal firm using 'agreements' instead of 'contracts'. Uses matter_number instead of contract_number. total_fees is the contract value."
    },
    "client_d": {
        "connection": {
            "type": "sqlite",
            "database": "data/databases/client_d.db"
        },
        "tables": {
            "vendor_contracts": {
                "columns": {
                    "contract_num": "VARCHAR(50) PRIMARY KEY",
                    "vendor_id": "INTEGER",
                    "contract_type": "VARCHAR(100)",
                    "annual_contract_value": "DECIMAL(15,2)",  # Annual, not total!
                    "contract_term_years": "INTEGER",
                    "days_since_start": "INTEGER",  # Not a date!
                    "days_until_expiry": "INTEGER",  # Not a date!
                    "auto_renew_flag": "INTEGER",  # 0 or 1
                    "payment_terms": "VARCHAR(100)"
                }
            },
            "vendors": {
                "columns": {
                    "vendor_id": "INTEGER PRIMARY KEY",
                    "vendor_name": "VARCHAR(200)",
                    "vendor_category": "VARCHAR(100)",
                    "country_code": "VARCHAR(3)"
                }
            },
            "contract_line_items": {
                "columns": {
                    "line_id": "INTEGER PRIMARY KEY",
                    "contract_num": "VARCHAR(50)",
                    "product_sku": "VARCHAR(100)",
                    "quantity": "INTEGER",
                    "unit_price": "DECIMAL(10,2)",
                    "line_total": "DECIMAL(15,2)"
                }
            }
        },
        "semantic_context": "Manufacturing company. annual_contract_value is annual (not total). Total value = annual_contract_value * contract_term_years. Uses days_since_start and days_until_expiry instead of dates. auto_renew_flag is 0/1 not boolean."
    }
}


class SchemaRepository:
    """
    Repository for accessing client (tenant) schemas
    Provides a clean interface for schema retrieval
    """

    def __init__(self, schemas: Dict[str, Any] = None):
        """
        Initialize repository with schemas

        Args:
            schemas: Client schemas dictionary (defaults to CLIENT_SCHEMAS)
        """
        self.schemas = schemas if schemas is not None else CLIENT_SCHEMAS

    def get_schema(self, client_id: str) -> Dict[str, Any]:
        """
        Get schema for a specific client (tenant)

        Args:
            client_id: Client identifier

        Returns:
            Client schema dictionary

        Raises:
            CustomerNotFoundError: If client_id not found
        """
        if client_id not in self.schemas:
            raise CustomerNotFoundError(client_id)
        return self.schemas[client_id]

    def get_canonical_schema(self) -> Dict[str, Any]:
        """
        Get the canonical (unified) schema

        Returns:
            Canonical schema dictionary
        """
        return CANONICAL_SCHEMA

    def list_clients(self) -> List[str]:
        """
        Get list of all client IDs

        Returns:
            List of client identifiers
        """
        return list(self.schemas.keys())

    def get_all_schemas(self) -> Dict[str, Any]:
        """
        Get all client schemas

        Returns:
            Dictionary mapping client IDs to schemas
        """
        return self.schemas


@lru_cache()
def get_schema_repository() -> SchemaRepository:
    """
    Get cached schema repository instance (singleton)

    Returns:
        SchemaRepository instance
    """
    return SchemaRepository()
