"""
Generate synthetic user data
"""

import random
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass


@dataclass
class UserProfile:
    """User profile for data generation"""

    user_id: str
    signup_date: datetime
    country: str
    tier: str  # bronze, silver, gold, platinum


class UserGenerator:
    """Generate synthetic user profiles"""

    COUNTRIES = ["US", "UK", "CA", "DE", "FR", "ES", "IT", "BR", "MX", "AU"]

    TIERS = ["bronze", "silver", "gold", "platinum"]
    TIER_WEIGHTS = [0.5, 0.3, 0.15, 0.05]  # Most users are bronze

    def __init__(self, total_users: int = 1000):
        self.total_users = total_users
        self.users: List[UserProfile] = []
        self._generate_users()

    def _generate_users(self):
        """Generate user profiles"""
        base_date = datetime.now() - timedelta(days=365)

        for i in range(1, self.total_users + 1):
            user_id = f"user_{i:06d}"

            # Signup date distributed over last year
            days_ago = random.randint(0, 365)
            signup_date = base_date + timedelta(days=days_ago)

            # Country distribution (weighted towards US)
            country = random.choices(
                self.COUNTRIES, weights=[0.4, 0.15, 0.1, 0.1, 0.08, 0.05, 0.05, 0.04, 0.02, 0.01]
            )[0]

            # Tier distribution
            tier = random.choices(self.TIERS, weights=self.TIER_WEIGHTS)[0]

            self.users.append(
                UserProfile(user_id=user_id, signup_date=signup_date, country=country, tier=tier)
            )

    def get_random_user(self) -> UserProfile:
        """Get a random user"""
        return random.choice(self.users)

    def get_active_users(self, count: int) -> List[UserProfile]:
        """Get random active users (weighted by tier - higher tier = more active)"""
        # Weight users by tier for more realistic activity
        weights = []
        for user in self.users:
            tier_weight = {"platinum": 4, "gold": 3, "silver": 2, "bronze": 1}[user.tier]
            weights.append(tier_weight)

        return random.choices(self.users, weights=weights, k=count)
