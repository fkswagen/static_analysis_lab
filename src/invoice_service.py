from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: Optional[str]
    items: List[LineItem]

class InvoiceService:
    def __init__(self) -> None:
        self._coupon_rate: Dict[str, float] = {
            "WELCOME10": 0.10, "VIP20": 0.20, "STUDENT5": 0.05
        }
      
        self._shipping_rules = {
            "TH": (500, 60), "JP": (4000, 600), "US": (300, 15), "DEFAULT": (200, 25)
        }

    def _validate(self, inv: Invoice) -> List[str]:
        if not inv: return ["Invoice is missing"]
        problems = []
        if not inv.invoice_id: problems.append("Missing invoice_id")
        if not inv.customer_id: problems.append("Missing customer_id")
        if not inv.items: problems.append("Invoice must contain items")
        
        for it in inv.items:
            if not it.sku: problems.append("Item sku is missing")
            if it.qty <= 0: problems.append(f"Invalid qty for {it.sku}")
            if it.unit_price < 0: problems.append(f"Invalid price for {it.sku}")
            if it.category not in ("book", "food", "electronics", "other"):
                problems.append(f"Unknown category for {it.sku}")
        return problems

    def _get_shipping(self, country: str, subtotal: float) -> float:
     
        limit, fee = self._shipping_rules.get(country, self._shipping_rules["DEFAULT"])
        if country == "US": # กรณีพิเศษของ US
            if subtotal < 100: return 15
            return 8 if subtotal < 300 else 0
        return fee if subtotal < limit else 0

    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        warnings: List[str] = []
        problems = self._validate(inv)
        if problems: raise ValueError("; ".join(problems))
        
        subtotal = sum(it.unit_price * it.qty for it in inv.items)
        fragile_fee = sum(5.0 * it.qty for it in inv.items if it.fragile)
        
        shipping = self._get_shipping(inv.country, subtotal)
            
        
        membership_discounts = {"gold": 0.03, "platinum": 0.05}
        discount = subtotal * membership_discounts.get(inv.membership, 0.0)
        if not discount and subtotal > 3000: discount = 20
        
        if inv.coupon and inv.coupon.strip() in self._coupon_rate:
            discount += subtotal * self._coupon_rate[inv.coupon.strip()]
        elif inv.coupon:
            warnings.append("Unknown coupon")
        
      
        tax_rates = {"TH": 0.07, "JP": 0.10, "US": 0.08}
        tax = (subtotal - discount) * tax_rates.get(inv.country, 0.05)
            
        total = max(0, subtotal + shipping + fragile_fee + tax - discount)
        if subtotal > 10000 and inv.membership not in ("gold", "platinum"):
            warnings.append("Consider membership upgrade")
            
        return total, warnings