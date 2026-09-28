"""CP3 — Cost guard: giới hạn chi phí theo user và tháng."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status


KEY_TTL_SECONDS = 40 * 24 * 3600


class CostGuard:
    def __init__(self, client, monthly_budget_usd: float) -> None:
        self.client = client
        self.budget = monthly_budget_usd

    @staticmethod
    def current_month() -> str:
        """Trả về tháng hiện tại theo UTC, dạng YYYY-MM."""
        return datetime.now(timezone.utc).strftime("%Y-%m")

    @classmethod
    def _key(
        cls,
        user_id: str,
        month: str | None = None,
    ) -> str:
        """Tạo Redis key riêng cho từng user và từng tháng."""
        return f"cost:{user_id}:{month or cls.current_month()}"

    def spent(
        self,
        user_id: str,
        month: str | None = None,
    ) -> float:
        """Đọc tổng chi phí user đã tiêu trong tháng."""
        key = self._key(user_id, month)
        value = self.client.get(key)

        if value is None:
            return 0.0

        return float(value)

    def check(
        self,
        user_id: str,
        estimated_cost: float = 0.0,
        month: str | None = None,
    ) -> None:
        """Chặn request nếu tổng chi phí vượt ngân sách."""
        total = self.spent(user_id, month) + estimated_cost

        if total > self.budget:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="monthly budget exceeded",
            )

    def record(
        self,
        user_id: str,
        cost: float,
        month: str | None = None,
    ) -> float:
        """Cộng chi phí vừa phát sinh và trả về tổng mới."""
        key = self._key(user_id, month)

        total = self.client.incrbyfloat(key, cost)
        self.client.expire(key, KEY_TTL_SECONDS)

        return float(total)