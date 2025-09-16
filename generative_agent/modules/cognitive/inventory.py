from typing import Dict, List, Any, Optional
import json

class InventoryItem:
    def __init__(self, item_dict: Dict[str, Any]):
        self.name = item_dict["name"]
        self.quantity = item_dict["quantity"]
        self.value = item_dict.get("value", 0.0)  # Value per unit
        self.description = item_dict.get("description", "")
        self.created = item_dict.get("created", 0)
        self.last_modified = item_dict.get("last_modified", 0)

    def get_total_value(self) -> float:
        """Get total value of all units of this item."""
        return self.quantity * self.value

    def package(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "value": self.value,
            "description": self.description,
            "created": self.created,
            "last_modified": self.last_modified
        }

class InventoryRecord:
    def __init__(self, record_dict: Dict[str, Any]):
        self.record_id = record_dict["record_id"]
        self.action = record_dict["action"]  # "add", "remove", "trade_failed", "receive_payment", "sell_item", "make_payment", "buy_item"
        self.item_name = record_dict["item_name"]
        self.quantity = record_dict["quantity"]
        self.time_step = record_dict["time_step"]
        self.description = record_dict.get("description", "")
        self.trade_partner = record_dict.get("trade_partner", "")

    def package(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "action": self.action,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "time_step": self.time_step,
            "description": self.description,
            "trade_partner": self.trade_partner
        }

class Inventory:
    def __init__(self, items_data: List[Dict[str, Any]] = None, records_data: List[Dict[str, Any]] = None):
        self.items: Dict[str, InventoryItem] = {}
        self.records: List[InventoryRecord] = []
        
        if items_data:
            for item_data in items_data:
                item = InventoryItem(item_data)
                self.items[item.name] = item
        
        if records_data:
            for record_data in records_data:
                record = InventoryRecord(record_data)
                self.records.append(record)
        

    def _add_record(self, action: str, item_name: str, quantity: int, time_step: int, description: str = "", trade_partner: str = ""):
        record_dict = {
            "record_id": len(self.records),
            "action": action,
            "item_name": item_name,
            "quantity": quantity,
            "time_step": time_step,
            "description": description,
            "trade_partner": trade_partner
        }
        record = InventoryRecord(record_dict)
        self.records.append(record)

    def add_item(self, name: str, quantity: int, time_step: int, value: float = 0.0, description: str = ""):
        if name in self.items:
            # When adding to existing item, keep the existing value unless new value is provided
            if value > 0.0:
                # Update the weighted average value
                old_total_value = self.items[name].get_total_value()
                new_total_value = quantity * value
                total_quantity = self.items[name].quantity + quantity
                self.items[name].value = (old_total_value + new_total_value) / total_quantity
            
            self.items[name].quantity += quantity
            self.items[name].last_modified = time_step
        else:
            item_dict = {
                "name": name,
                "quantity": quantity,
                "value": value,
                "description": description,
                "created": time_step,
                "last_modified": time_step
            }
            self.items[name] = InventoryItem(item_dict)
        
        self._add_record("add", name, quantity, time_step, description)

    def remove_item(self, name: str, quantity: int, time_step: int, description: str = "") -> bool:
        if name not in self.items:
            return False
        
        if self.items[name].quantity < quantity:
            return False
        
        self.items[name].quantity -= quantity
        self.items[name].last_modified = time_step
        
        
        self._add_record("remove", name, quantity, time_step, description)
        return True

    def trade_item(self, item_name: str, quantity: int, is_giving: bool, time_step: int, trade_partner: str = "", value: float = 0.0, description: str = "") -> bool:
        if is_giving:
            # Use sell_item for giving items (more specific than generic trade_give)
            return self.sell_item(item_name, quantity, time_step, trade_partner, 0.0, description)
        else:
            # Use buy_item for receiving items (more specific than generic trade_receive)  
            return self.buy_item(item_name, quantity, time_step, trade_partner, value, description)
    
    def record_trade_failure(self, item_name: str, quantity: int, time_step: int, trade_partner: str = "", reason: str = ""):
        """Record a failed trade attempt."""
        description = f"Failed to trade {quantity} {item_name}" + (f" with {trade_partner}" if trade_partner else "") + (f": {reason}" if reason else "")
        self._add_record("trade_failed", item_name, quantity, time_step, description, trade_partner)

    def receive_payment(self, payment_amount: int, time_step: int, payer: str = "", description: str = ""):
        """Record receiving payment (typically digital cash)."""
        self.add_item("digital cash", payment_amount, time_step, 1.0, description)
        self.records[-1].action = "receive_payment"
        self.records[-1].trade_partner = payer
        return True

    def sell_item(self, item_name: str, quantity: int, time_step: int, buyer: str = "", price_per_unit: float = 0.0, description: str = "") -> bool:
        """Record selling an item (removes from inventory)."""
        success = self.remove_item(item_name, quantity, time_step, description)
        if success:
            self.records[-1].action = "sell_item"
            self.records[-1].trade_partner = buyer
            # Also record receiving payment if price is specified
            if price_per_unit > 0:
                total_payment = quantity * price_per_unit
                self.receive_payment(int(total_payment), time_step, buyer, f"Payment for {quantity} {item_name}")
        return success

    def make_payment(self, payment_amount: int, time_step: int, recipient: str = "", description: str = "") -> bool:
        """Record making a payment (removes digital cash from inventory)."""
        success = self.remove_item("digital cash", payment_amount, time_step, description)
        if success:
            self.records[-1].action = "make_payment"
            self.records[-1].trade_partner = recipient
        return success

    def buy_item(self, item_name: str, quantity: int, time_step: int, seller: str = "", price_per_unit: float = 0.0, description: str = ""):
        """Record buying an item (adds to inventory)."""
        self.add_item(item_name, quantity, time_step, price_per_unit, description)
        self.records[-1].action = "buy_item"
        self.records[-1].trade_partner = seller
        # Also record making payment if price is specified
        if price_per_unit > 0:
            total_payment = quantity * price_per_unit
            self.make_payment(int(total_payment), time_step, seller, f"Payment for {quantity} {item_name}")
        return True

    def get_item_quantity(self, name: str) -> int:
        return self.items[name].quantity if name in self.items else 0

    def has_item(self, name: str, minimum_quantity: int = 1) -> bool:
        return name in self.items and self.items[name].quantity >= minimum_quantity

    def get_item_value(self, name: str) -> float:
        """Get the value per unit of a specific item."""
        return self.items[name].value if name in self.items else 0.0

    def get_item_total_value(self, name: str) -> float:
        """Get the total value of all units of a specific item."""
        return self.items[name].get_total_value() if name in self.items else 0.0

    def get_all_items(self) -> Dict[str, int]:
        return {name: item.quantity for name, item in self.items.items()}

    def get_all_items_with_values(self) -> Dict[str, Dict[str, float]]:
        """Get all items with their quantities and values."""
        return {name: {
            "quantity": item.quantity, 
            "value_per_unit": item.value,
            "total_value": item.get_total_value()
        } for name, item in self.items.items()}

    def get_total_items_count(self) -> int:
        return sum(item.quantity for item in self.items.values())

    def get_total_inventory_value(self) -> float:
        """Get the total value of entire inventory."""
        return sum(item.get_total_value() for item in self.items.values())

    def get_unique_items_count(self) -> int:
        return len(self.items)

    def get_trade_history(self, item_name: str = None) -> List[Dict[str, Any]]:
        """Get history of trading transactions (now includes sell_item and buy_item)."""
        trades = []
        for record in self.records:
            if record.action in ["sell_item", "buy_item"]:
                if item_name is None or record.item_name == item_name:
                    trades.append(record.package())
        return trades
    
    def get_failed_trade_history(self, item_name: str = None) -> List[Dict[str, Any]]:
        """Get history of failed trade attempts."""
        failed_trades = []
        for record in self.records:
            if record.action == "trade_failed":
                if item_name is None or record.item_name == item_name:
                    failed_trades.append(record.package())
        return failed_trades
    
    def get_payment_history(self, item_name: str = None) -> List[Dict[str, Any]]:
        """Get history of payments (both made and received)."""
        payments = []
        for record in self.records:
            if record.action in ["receive_payment", "make_payment"]:
                if item_name is None or record.item_name == item_name:
                    payments.append(record.package())
        return payments
    
    def get_sales_history(self, item_name: str = None) -> List[Dict[str, Any]]:
        """Get history of sales transactions."""
        sales = []
        for record in self.records:
            if record.action == "sell_item":
                if item_name is None or record.item_name == item_name:
                    sales.append(record.package())
        return sales
    
    def get_purchase_history(self, item_name: str = None) -> List[Dict[str, Any]]:
        """Get history of purchase transactions."""
        purchases = []
        for record in self.records:
            if record.action == "buy_item":
                if item_name is None or record.item_name == item_name:
                    purchases.append(record.package())
        return purchases
    
    def get_transaction_summary(self) -> Dict[str, int]:
        """Get a summary count of all transaction types."""
        summary = {
            "sell_item": 0,
            "buy_item": 0,
            "receive_payment": 0,
            "make_payment": 0,
            "trade_failed": 0,
            "add": 0,
            "remove": 0
        }
        
        for record in self.records:
            if record.action in summary:
                summary[record.action] += 1
        
        return summary
    
    def package(self) -> Dict[str, Any]:
        return {
            "items": [item.package() for item in self.items.values()],
            "records": [record.package() for record in self.records],
        }
