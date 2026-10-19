from typing import List, Literal, Optional, TypedDict

from ._base import Resource
from .types import DeletedResponse, PaginationParams

DomainTLSPolicy = Literal["OPTIONAL", "REQUIRE"]
DNSRecordType = Literal["CNAME", "TXT", "MX"]


class UpdateDomainParams(TypedDict, total=False):
    inboundPrefix: str
    email: str
    senderName: str
    clickTracking: bool
    openTracking: bool
    tlsPolicy: DomainTLSPolicy
    inboundEnabled: bool


class _CreateDomainParamsRequired(TypedDict):
    domain: str
    email: str


class CreateDomainParams(_CreateDomainParamsRequired, total=False):
    senderName: str
    region: str


class DNSRecord(TypedDict):
    type: DNSRecordType
    name: str
    fqdn: str
    value: str


class DomainSummary(TypedDict):
    id: str
    domain: str
    email: str
    senderName: Optional[str]
    region: str
    verified: bool
    clickTracking: bool
    openTracking: bool
    tlsPolicy: DomainTLSPolicy
    inboundEnabled: bool
    inboundVerified: bool
    inboundPrefix: str
    projectId: str
    createdAt: str
    updatedAt: str


class DomainRead(DomainSummary, total=False):
    verificationToken: str
    dkimTokens: List[str]
    dnsRecords: List[DNSRecord]


class ListDomainsParams(PaginationParams, total=False):
    verified: bool


class _ListDomainsResponseRequired(TypedDict):
    items: List[DomainSummary]


class ListDomainsResponse(_ListDomainsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class InboundMXRecord(TypedDict):
    exchange: str
    priority: int


class InboundVerifyResult(DomainRead):
    inboundMxResolved: List[InboundMXRecord]
    inboundExpectedTarget: str


class DNSRecordsResponse(TypedDict):
    items: List[DNSRecord]


class DomainRegionsResponse(TypedDict):
    items: List[str]


class Domains(Resource):
    """Domains API resource"""

    def list(self, params: Optional[ListDomainsParams] = None) -> ListDomainsResponse:
        """List sending domains with cursor or explicit page pagination."""
        return self._client.get("/domains", params)

    def get(self, domain_id: str) -> DomainRead:
        """Retrieve a domain and its current verification state."""
        return self._client.get(f"/domains/{domain_id}")

    def create(self, data: CreateDomainParams) -> DomainRead:
        """Register a domain; DNS material requires domain:dns-read."""
        return self._client.post("/domains", data)

    def update(self, domain_id: str, data: UpdateDomainParams) -> DomainRead:
        """Update domain sending, tracking, TLS, or inbound settings."""
        return self._client.put(f"/domains/{domain_id}", data)

    def delete(self, domain_id: str) -> DeletedResponse:
        """Delete a domain after the API confirms it is safe to remove."""
        return self._client.delete(f"/domains/{domain_id}")

    def verify(self, domain_id: str) -> DomainRead:
        """Recheck sending DNS records and return the updated domain state."""
        return self._client.post(f"/domains/{domain_id}/verify")

    def verify_inbound(self, domain_id: str) -> InboundVerifyResult:
        """Check the inbound MX record and return details useful for diagnosis."""
        return self._client.post(f"/domains/{domain_id}/inbound/verify")

    def dns_records(self, domain_id: str) -> DNSRecordsResponse:
        """Return the DNS records required for sending and inbound mail."""
        return self._client.get(f"/domains/{domain_id}/dns-records")

    def regions(self) -> DomainRegionsResponse:
        """List region identifiers accepted when registering a domain."""
        return self._client.get("/domains/regions")
