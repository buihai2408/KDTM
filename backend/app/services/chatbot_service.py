"""
Chatbot Service
Handles intent detection, safe query execution, and response generation
for Dify Cloud integration
"""
import re
from datetime import datetime, date
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


# =============================================================================
# ALLOWLIST OF SAFE VIEWS (Security Layer)
# =============================================================================
ALLOWED_VIEWS = [
    "v_income_vs_expense",
    "v_monthly_summary", 
    "v_category_breakdown",
    "v_budget_vs_actual",
    "v_wallet_balance",
    "v_recent_transactions",
    "v_daily_summary"
]


# =============================================================================
# INTENT PATTERNS (Vietnamese & English)
# =============================================================================
INTENT_PATTERNS = {
    "total_expense": [
        r"tổng\s*(chi\s*tiêu|chi)",
        r"chi\s*tiêu\s*tổng",
        r"total\s*expense",
        r"spending\s*total",
        r"bao\s*nhiêu\s*tiền\s*(đã\s*)?chi",
        r"đã\s*chi\s*bao\s*nhiêu",
    ],
    "total_income": [
        r"tổng\s*(thu\s*nhập|thu)",
        r"thu\s*nhập\s*tổng",
        r"total\s*income",
        r"earnings?\s*total",
        r"bao\s*nhiêu\s*tiền\s*(đã\s*)?(nhận|thu)",
        r"đã\s*(nhận|thu)\s*bao\s*nhiêu",
    ],
    "category_breakdown": [
        r"chi\s*tiêu\s*(theo|từng)\s*danh\s*mục",
        r"danh\s*mục\s*chi\s*tiêu",
        r"(spending|expense)\s*by\s*category",
        r"category\s*(breakdown|summary)",
        r"tiền\s*(đi\s*đâu|vào\s*đâu)",
        r"chi\s*nhiều\s*nhất\s*(vào\s*)?đâu",
    ],
    "monthly_trend": [
        r"xu\s*hướng\s*(hàng\s*)?tháng",
        r"so\s*sánh\s*(các\s*)?tháng",
        r"monthly\s*trend",
        r"trend\s*analysis",
        r"biến\s*động\s*(theo\s*)?tháng",
        r"tháng\s*này\s*so\s*(với\s*)?tháng\s*trước",
    ],
    "budget_status": [
        r"ngân\s*sách",
        r"budget",
        r"vượt\s*(ngân\s*sách|chi)",
        r"over\s*budget",
        r"còn\s*bao\s*nhiêu\s*(ngân\s*sách)?",
        r"hết\s*ngân\s*sách\s*chưa",
    ],
    "recent_transactions": [
        r"giao\s*dịch\s*(gần\s*đây|mới)",
        r"recent\s*transactions?",
        r"latest\s*transactions?",
        r"(các\s*)?khoản\s*chi\s*(gần\s*đây|mới)",
        r"chi\s*gì\s*gần\s*đây",
    ],
    "wallet_balance": [
        r"số\s*dư(\s*ví)?",
        r"balance",
        r"wallet",
        r"còn\s*bao\s*nhiêu\s*tiền",
        r"tiền\s*trong\s*ví",
        r"ví\s*còn\s*bao\s*nhiêu",
    ],
    "income_vs_expense": [
        r"thu\s*chi",
        r"income\s*(vs|versus|and)\s*expense",
        r"so\s*sánh\s*thu\s*chi",
        r"cân\s*đối\s*thu\s*chi",
        r"tiết\s*kiệm\s*(được\s*)?bao\s*nhiêu",
        r"savings?",
    ],
    "daily_summary": [
        r"(chi\s*tiêu\s*)?hôm\s*nay",
        r"today('?s)?\s*(spending|expense)",
        r"daily\s*summary",
        r"ngày\s*hôm\s*nay",
    ],
}


# =============================================================================
# TIME EXTRACTION PATTERNS
# =============================================================================
TIME_PATTERNS = {
    "this_month": [
        r"tháng\s*này",
        r"this\s*month",
        r"tháng\s*hiện\s*tại",
        r"current\s*month",
    ],
    "last_month": [
        r"tháng\s*(trước|rồi)",
        r"last\s*month",
        r"previous\s*month",
    ],
    "this_year": [
        r"năm\s*nay",
        r"this\s*year",
        r"năm\s*hiện\s*tại",
    ],
    "specific_month": [
        r"tháng\s*(\d{1,2})",
        r"month\s*(\d{1,2})",
        r"(\d{1,2})/(\d{4})",
    ],
    "today": [
        r"hôm\s*nay",
        r"today",
        r"ngày\s*hôm\s*nay",
    ],
    "yesterday": [
        r"hôm\s*qua",
        r"yesterday",
    ],
    "this_week": [
        r"tuần\s*này",
        r"this\s*week",
    ],
}


class ChatbotService:
    """Service class for chatbot operations"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def detect_intent(self, question: str) -> Tuple[str, float]:
        """
        Detect the user's intent from their question
        Returns: (intent_name, confidence_score)
        """
        question_lower = question.lower().strip()
        
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return intent, 0.9
        
        # Default fallback
        return "unknown", 0.0
    
    def extract_time_context(self, question: str) -> Dict[str, Any]:
        """
        Extract time context from the question
        Returns dict with year, month, date_range, etc.
        """
        question_lower = question.lower()
        now = datetime.now()
        
        context = {
            "year": now.year,
            "month": now.month,
            "time_type": "this_month",
            "specified": False,
        }
        
        # Check for "this month"
        for pattern in TIME_PATTERNS["this_month"]:
            if re.search(pattern, question_lower):
                context["time_type"] = "this_month"
                context["specified"] = True
                return context
        
        # Check for "last month"
        for pattern in TIME_PATTERNS["last_month"]:
            if re.search(pattern, question_lower):
                if now.month == 1:
                    context["year"] = now.year - 1
                    context["month"] = 12
                else:
                    context["month"] = now.month - 1
                context["time_type"] = "last_month"
                context["specified"] = True
                return context
        
        # Check for specific month number (e.g., "tháng 5")
        for pattern in TIME_PATTERNS["specific_month"]:
            match = re.search(pattern, question_lower)
            if match:
                month_num = int(match.group(1))
                if 1 <= month_num <= 12:
                    context["month"] = month_num
                    context["time_type"] = "specific_month"
                    context["specified"] = True
                    return context
        
        # Check for today
        for pattern in TIME_PATTERNS["today"]:
            if re.search(pattern, question_lower):
                context["time_type"] = "today"
                context["date"] = now.date()
                context["specified"] = True
                return context
        
        # Check for this year
        for pattern in TIME_PATTERNS["this_year"]:
            if re.search(pattern, question_lower):
                context["time_type"] = "this_year"
                context["specified"] = True
                return context
        
        return context
    
    def query_income_vs_expense(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Query income vs expense for a specific month"""
        query = text("""
            SELECT 
                total_income,
                total_expense,
                net_savings,
                expense_ratio
            FROM v_income_vs_expense
            WHERE user_id = :user_id 
              AND year = :year 
              AND month = :month
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "year": year,
            "month": month
        }).fetchone()
        
        if result:
            return {
                "total_income": float(result.total_income or 0),
                "total_expense": float(result.total_expense or 0),
                "net_savings": float(result.net_savings or 0),
                "expense_ratio": float(result.expense_ratio or 0),
                "year": year,
                "month": month,
            }
        return {
            "total_income": 0,
            "total_expense": 0,
            "net_savings": 0,
            "expense_ratio": 0,
            "year": year,
            "month": month,
        }
    
    def query_category_breakdown(self, user_id: int, year: int, month: int, 
                                  transaction_type: str = "expense") -> List[Dict[str, Any]]:
        """Query category breakdown for a specific month"""
        query = text("""
            SELECT 
                category_name,
                category_icon,
                category_color,
                total_amount,
                transaction_count,
                percentage
            FROM v_category_breakdown
            WHERE user_id = :user_id 
              AND year = :year 
              AND month = :month
              AND type = :type
            ORDER BY total_amount DESC
            LIMIT 10
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "year": year,
            "month": month,
            "type": transaction_type
        }).fetchall()
        
        return [
            {
                "category_name": row.category_name,
                "category_icon": row.category_icon,
                "total_amount": float(row.total_amount),
                "transaction_count": row.transaction_count,
                "percentage": float(row.percentage or 0),
            }
            for row in result
        ]
    
    def query_budget_status(self, user_id: int, year: int, month: int) -> List[Dict[str, Any]]:
        """Query budget vs actual spending"""
        query = text("""
            SELECT 
                category_name,
                category_icon,
                category_color,
                budget_amount,
                actual_spent,
                remaining,
                usage_percentage,
                status
            FROM v_budget_vs_actual
            WHERE user_id = :user_id 
              AND year = :year 
              AND month = :month
            ORDER BY usage_percentage DESC
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "year": year,
            "month": month
        }).fetchall()
        
        return [
            {
                "category_name": row.category_name,
                "budget_amount": float(row.budget_amount),
                "actual_spent": float(row.actual_spent),
                "remaining": float(row.remaining),
                "usage_percentage": float(row.usage_percentage or 0),
                "status": row.status,
            }
            for row in result
        ]
    
    def query_wallet_balance(self, user_id: int) -> List[Dict[str, Any]]:
        """Query wallet balances"""
        query = text("""
            SELECT 
                wallet_name,
                wallet_icon,
                currency,
                current_balance,
                total_income,
                total_expense,
                transaction_count
            FROM v_wallet_balance
            WHERE user_id = :user_id
            ORDER BY current_balance DESC
        """)
        
        result = self.db.execute(query, {"user_id": user_id}).fetchall()
        
        return [
            {
                "wallet_name": row.wallet_name,
                "currency": row.currency,
                "current_balance": float(row.current_balance),
                "total_income": float(row.total_income),
                "total_expense": float(row.total_expense),
                "transaction_count": row.transaction_count,
            }
            for row in result
        ]
    
    def query_recent_transactions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Query recent transactions"""
        query = text("""
            SELECT 
                transaction_id,
                type,
                amount,
                description,
                transaction_date,
                category_name,
                category_icon,
                wallet_name
            FROM v_recent_transactions
            WHERE user_id = :user_id
            ORDER BY transaction_date DESC, created_at DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "limit": limit
        }).fetchall()
        
        return [
            {
                "transaction_id": row.transaction_id,
                "type": row.type,
                "amount": float(row.amount),
                "description": row.description,
                "transaction_date": row.transaction_date.strftime("%Y-%m-%d") if row.transaction_date else None,
                "category_name": row.category_name,
                "wallet_name": row.wallet_name,
            }
            for row in result
        ]
    
    def query_monthly_summary(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Query monthly summary"""
        query = text("""
            SELECT 
                type,
                transaction_count,
                total_amount,
                avg_amount,
                max_amount
            FROM v_monthly_summary
            WHERE user_id = :user_id 
              AND year = :year 
              AND month = :month
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "year": year,
            "month": month
        }).fetchall()
        
        summary = {
            "year": year,
            "month": month,
            "income": {"total": 0, "count": 0, "avg": 0},
            "expense": {"total": 0, "count": 0, "avg": 0},
        }
        
        for row in result:
            if row.type == "income":
                summary["income"] = {
                    "total": float(row.total_amount or 0),
                    "count": row.transaction_count,
                    "avg": float(row.avg_amount or 0),
                }
            elif row.type == "expense":
                summary["expense"] = {
                    "total": float(row.total_amount or 0),
                    "count": row.transaction_count,
                    "avg": float(row.avg_amount or 0),
                }
        
        return summary
    
    def query_daily_summary(self, user_id: int, target_date: date) -> Dict[str, Any]:
        """Query daily summary"""
        query = text("""
            SELECT 
                type,
                transaction_count,
                total_amount
            FROM v_daily_summary
            WHERE user_id = :user_id 
              AND transaction_date = :target_date
        """)
        
        result = self.db.execute(query, {
            "user_id": user_id,
            "target_date": target_date
        }).fetchall()
        
        summary = {
            "date": target_date.strftime("%Y-%m-%d"),
            "income": 0,
            "expense": 0,
            "income_count": 0,
            "expense_count": 0,
        }
        
        for row in result:
            if row.type == "income":
                summary["income"] = float(row.total_amount or 0)
                summary["income_count"] = row.transaction_count
            elif row.type == "expense":
                summary["expense"] = float(row.total_amount or 0)
                summary["expense_count"] = row.transaction_count
        
        return summary
    
    def format_currency(self, amount: float, currency: str = "VND") -> str:
        """Format amount as currency string"""
        if currency == "VND":
            return f"{amount:,.0f} VND"
        return f"{amount:,.2f} {currency}"
    
    def get_month_name_vi(self, month: int) -> str:
        """Get Vietnamese month name"""
        return f"tháng {month}"
    
    def process_query(self, user_id: int, question: str, timezone: str = "Asia/Bangkok") -> Dict[str, Any]:
        """
        Main entry point - process a user question and return an answer
        """
        # Detect intent
        intent, confidence = self.detect_intent(question)
        
        # Extract time context
        time_context = self.extract_time_context(question)
        year = time_context["year"]
        month = time_context["month"]
        
        # Process based on intent
        if intent == "total_expense":
            return self._handle_total_expense(user_id, year, month)
        
        elif intent == "total_income":
            return self._handle_total_income(user_id, year, month)
        
        elif intent == "category_breakdown":
            return self._handle_category_breakdown(user_id, year, month)
        
        elif intent == "budget_status":
            return self._handle_budget_status(user_id, year, month)
        
        elif intent == "wallet_balance":
            return self._handle_wallet_balance(user_id)
        
        elif intent == "recent_transactions":
            return self._handle_recent_transactions(user_id)
        
        elif intent == "income_vs_expense":
            return self._handle_income_vs_expense(user_id, year, month)
        
        elif intent == "monthly_trend":
            return self._handle_monthly_trend(user_id, year)
        
        elif intent == "daily_summary":
            target_date = time_context.get("date", datetime.now().date())
            return self._handle_daily_summary(user_id, target_date)
        
        else:
            return self._handle_unknown(question, time_context)
    
    def _handle_total_expense(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Handle total expense query"""
        data = self.query_income_vs_expense(user_id, year, month)
        expense = data["total_expense"]
        month_name = self.get_month_name_vi(month)
        
        if expense == 0:
            answer = f"📊 Bạn chưa có chi tiêu nào trong {month_name}/{year}."
        else:
            answer = f"💸 Tổng chi tiêu {month_name}/{year} của bạn là **{self.format_currency(expense)}**."
        
        return {
            "answer": answer,
            "data": data,
            "suggested_actions": [
                "Xem chi tiết theo danh mục",
                "So sánh với tháng trước",
                "Kiểm tra ngân sách",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_total_income(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Handle total income query"""
        data = self.query_income_vs_expense(user_id, year, month)
        income = data["total_income"]
        month_name = self.get_month_name_vi(month)
        
        if income == 0:
            answer = f"📊 Bạn chưa có thu nhập nào trong {month_name}/{year}."
        else:
            answer = f"💰 Tổng thu nhập {month_name}/{year} của bạn là **{self.format_currency(income)}**."
        
        return {
            "answer": answer,
            "data": data,
            "suggested_actions": [
                "Xem chi tiết theo nguồn thu",
                "So sánh với tháng trước",
                "Xem tỷ lệ tiết kiệm",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_category_breakdown(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Handle category breakdown query"""
        categories = self.query_category_breakdown(user_id, year, month, "expense")
        month_name = self.get_month_name_vi(month)
        
        if not categories:
            answer = f"📊 Bạn chưa có chi tiêu nào trong {month_name}/{year}."
            return {
                "answer": answer,
                "data": {"categories": []},
                "suggested_actions": ["Thêm giao dịch mới", "Xem các tháng khác"]
            }
        
        # Build answer with top categories
        answer_parts = [f"📊 **Chi tiêu theo danh mục {month_name}/{year}:**\n"]
        for i, cat in enumerate(categories[:5], 1):
            amount_str = self.format_currency(cat["total_amount"])
            pct = cat["percentage"]
            answer_parts.append(f"{i}. **{cat['category_name']}**: {amount_str} ({pct:.1f}%)")
        
        answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": {"categories": categories, "year": year, "month": month},
            "suggested_actions": [
                "Xem chi tiết từng danh mục",
                "Đặt ngân sách cho danh mục",
                "So sánh với tháng trước",
                f"🔗 Xem biểu đồ: http://localhost:8088"
            ]
        }
    
    def _handle_budget_status(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Handle budget status query"""
        budgets = self.query_budget_status(user_id, year, month)
        month_name = self.get_month_name_vi(month)
        
        if not budgets:
            answer = f"📋 Bạn chưa thiết lập ngân sách cho {month_name}/{year}. Hãy tạo ngân sách để quản lý chi tiêu tốt hơn!"
            return {
                "answer": answer,
                "data": {"budgets": []},
                "suggested_actions": ["Tạo ngân sách mới", "Xem hướng dẫn thiết lập ngân sách"]
            }
        
        # Analyze budget status
        exceeded = [b for b in budgets if b["status"] == "exceeded"]
        warning = [b for b in budgets if b["status"] == "warning"]
        safe = [b for b in budgets if b["status"] == "safe"]
        
        answer_parts = [f"📋 **Tình trạng ngân sách {month_name}/{year}:**\n"]
        
        if exceeded:
            answer_parts.append(f"⚠️ **Vượt ngân sách ({len(exceeded)}):**")
            for b in exceeded[:3]:
                over = b["actual_spent"] - b["budget_amount"]
                answer_parts.append(f"  • {b['category_name']}: vượt {self.format_currency(over)} ({b['usage_percentage']:.0f}%)")
        
        if warning:
            answer_parts.append(f"\n⚡ **Cảnh báo ({len(warning)}):**")
            for b in warning[:3]:
                answer_parts.append(f"  • {b['category_name']}: {b['usage_percentage']:.0f}% ngân sách")
        
        if safe:
            answer_parts.append(f"\n✅ **An toàn ({len(safe)}):**")
            for b in safe[:3]:
                answer_parts.append(f"  • {b['category_name']}: còn {self.format_currency(b['remaining'])}")
        
        answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": {"budgets": budgets, "exceeded_count": len(exceeded), "warning_count": len(warning)},
            "suggested_actions": [
                "Điều chỉnh ngân sách",
                "Xem chi tiết chi tiêu",
                "Đặt cảnh báo ngân sách",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_wallet_balance(self, user_id: int) -> Dict[str, Any]:
        """Handle wallet balance query"""
        wallets = self.query_wallet_balance(user_id)
        
        if not wallets:
            answer = "💳 Bạn chưa có ví nào. Hãy tạo ví đầu tiên để bắt đầu quản lý tài chính!"
            return {
                "answer": answer,
                "data": {"wallets": []},
                "suggested_actions": ["Tạo ví mới"]
            }
        
        total_balance = sum(w["current_balance"] for w in wallets)
        
        answer_parts = [f"💳 **Số dư các ví của bạn:**\n"]
        answer_parts.append(f"📊 **Tổng số dư: {self.format_currency(total_balance)}**\n")
        
        for w in wallets:
            balance_str = self.format_currency(w["current_balance"], w["currency"])
            answer_parts.append(f"• **{w['wallet_name']}**: {balance_str}")
        
        answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": {"wallets": wallets, "total_balance": total_balance},
            "suggested_actions": [
                "Xem lịch sử giao dịch",
                "Chuyển tiền giữa các ví",
                "Thêm giao dịch mới",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_recent_transactions(self, user_id: int) -> Dict[str, Any]:
        """Handle recent transactions query"""
        transactions = self.query_recent_transactions(user_id, limit=10)
        
        if not transactions:
            answer = "📝 Bạn chưa có giao dịch nào. Hãy thêm giao dịch đầu tiên!"
            return {
                "answer": answer,
                "data": {"transactions": []},
                "suggested_actions": ["Thêm giao dịch thu nhập", "Thêm giao dịch chi tiêu"]
            }
        
        answer_parts = ["📝 **Giao dịch gần đây:**\n"]
        
        for t in transactions[:5]:
            icon = "💰" if t["type"] == "income" else "💸"
            amount_str = self.format_currency(t["amount"])
            date_str = t["transaction_date"]
            desc = t["description"] or t["category_name"]
            answer_parts.append(f"{icon} {date_str}: **{desc}** - {amount_str}")
        
        if len(transactions) > 5:
            answer_parts.append(f"\n... và {len(transactions) - 5} giao dịch khác")
        
        answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": {"transactions": transactions},
            "suggested_actions": [
                "Xem tất cả giao dịch",
                "Lọc theo danh mục",
                "Xuất báo cáo",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_income_vs_expense(self, user_id: int, year: int, month: int) -> Dict[str, Any]:
        """Handle income vs expense comparison"""
        data = self.query_income_vs_expense(user_id, year, month)
        month_name = self.get_month_name_vi(month)
        
        income = data["total_income"]
        expense = data["total_expense"]
        savings = data["net_savings"]
        
        if income == 0 and expense == 0:
            answer = f"📊 Bạn chưa có giao dịch nào trong {month_name}/{year}."
        else:
            answer_parts = [f"📊 **Tổng quan tài chính {month_name}/{year}:**\n"]
            answer_parts.append(f"💰 Thu nhập: **{self.format_currency(income)}**")
            answer_parts.append(f"💸 Chi tiêu: **{self.format_currency(expense)}**")
            
            if savings >= 0:
                answer_parts.append(f"✅ Tiết kiệm: **{self.format_currency(savings)}**")
                if income > 0:
                    savings_rate = (savings / income) * 100
                    answer_parts.append(f"📈 Tỷ lệ tiết kiệm: **{savings_rate:.1f}%**")
            else:
                answer_parts.append(f"⚠️ Chi vượt thu: **{self.format_currency(abs(savings))}**")
            
            answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": data,
            "suggested_actions": [
                "Xem chi tiết theo danh mục",
                "So sánh với tháng trước",
                "Thiết lập ngân sách",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_monthly_trend(self, user_id: int, year: int) -> Dict[str, Any]:
        """Handle monthly trend query"""
        # Query last 6 months
        query = text("""
            SELECT 
                year,
                month,
                total_income,
                total_expense,
                net_savings
            FROM v_income_vs_expense
            WHERE user_id = :user_id
            ORDER BY year DESC, month DESC
            LIMIT 6
        """)
        
        result = self.db.execute(query, {"user_id": user_id}).fetchall()
        
        if not result:
            answer = "📈 Chưa có dữ liệu để phân tích xu hướng. Hãy thêm giao dịch để xem báo cáo!"
            return {
                "answer": answer,
                "data": {"months": []},
                "suggested_actions": ["Thêm giao dịch"]
            }
        
        months_data = [
            {
                "year": row.year,
                "month": row.month,
                "income": float(row.total_income or 0),
                "expense": float(row.total_expense or 0),
                "savings": float(row.net_savings or 0),
            }
            for row in result
        ]
        
        # Reverse to show oldest first
        months_data.reverse()
        
        answer_parts = ["📈 **Xu hướng tài chính 6 tháng gần đây:**\n"]
        
        for m in months_data:
            month_name = f"T{m['month']}/{m['year']}"
            emoji = "✅" if m["savings"] >= 0 else "⚠️"
            answer_parts.append(f"{emoji} {month_name}: Thu {self.format_currency(m['income'])} | Chi {self.format_currency(m['expense'])}")
        
        # Calculate average
        avg_expense = sum(m["expense"] for m in months_data) / len(months_data)
        answer_parts.append(f"\n📊 Chi tiêu trung bình: **{self.format_currency(avg_expense)}/tháng**")
        
        answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": {"months": months_data},
            "suggested_actions": [
                "Xem chi tiết từng tháng",
                "Xem dự báo chi tiêu",
                "Đặt mục tiêu tiết kiệm",
                f"🔗 Xem biểu đồ: http://localhost:8088"
            ]
        }
    
    def _handle_daily_summary(self, user_id: int, target_date: date) -> Dict[str, Any]:
        """Handle daily summary query"""
        data = self.query_daily_summary(user_id, target_date)
        date_str = target_date.strftime("%d/%m/%Y")
        
        if data["income"] == 0 and data["expense"] == 0:
            answer = f"📅 Chưa có giao dịch nào ngày {date_str}."
        else:
            answer_parts = [f"📅 **Tổng quan ngày {date_str}:**\n"]
            
            if data["income"] > 0:
                answer_parts.append(f"💰 Thu nhập: {self.format_currency(data['income'])} ({data['income_count']} giao dịch)")
            
            if data["expense"] > 0:
                answer_parts.append(f"💸 Chi tiêu: {self.format_currency(data['expense'])} ({data['expense_count']} giao dịch)")
            
            net = data["income"] - data["expense"]
            if net >= 0:
                answer_parts.append(f"✅ Kết quả: +{self.format_currency(net)}")
            else:
                answer_parts.append(f"⚠️ Kết quả: -{self.format_currency(abs(net))}")
            
            answer = "\n".join(answer_parts)
        
        return {
            "answer": answer,
            "data": data,
            "suggested_actions": [
                "Xem chi tiết giao dịch",
                "Thêm giao dịch mới",
                "Xem tổng kết tuần",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def _handle_unknown(self, question: str, time_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown/unrecognized queries"""
        answer = """🤔 Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi tôi về:

📊 **Tổng quan tài chính:**
• "Tổng chi tiêu tháng này là bao nhiêu?"
• "Thu nhập tháng này của tôi?"
• "Tiết kiệm được bao nhiêu?"

💳 **Số dư và ví:**
• "Số dư trong ví?"
• "Còn bao nhiêu tiền?"

📋 **Ngân sách:**
• "Kiểm tra ngân sách"
• "Có vượt ngân sách không?"

📈 **Phân tích:**
• "Chi tiêu theo danh mục"
• "Xu hướng chi tiêu hàng tháng"

📝 **Giao dịch:**
• "Giao dịch gần đây"
• "Chi gì hôm nay?"

💡 Bạn có thể thêm thời gian vào câu hỏi, ví dụ: "tháng này", "tháng trước", "tháng 5"."""
        
        return {
            "answer": answer,
            "data": None,
            "suggested_actions": [
                "Tổng chi tiêu tháng này",
                "Kiểm tra ngân sách",
                "Số dư trong ví",
                "Giao dịch gần đây",
                f"🔗 Xem dashboard: http://localhost:8088"
            ]
        }
    
    def get_available_views(self) -> List[str]:
        """Return list of allowed views for transparency"""
        return ALLOWED_VIEWS.copy()
