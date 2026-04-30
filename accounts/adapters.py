from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """Account adapter that handles our custom User model with no username."""

    def populate_username(self, request, user):
        # Our User model has no username field, so skip this entirely.
        pass


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Social account adapter that handles our custom User model with no username."""

    def populate_user(self, request, sociallogin, data):
        """Populate user fields from social login data."""
        user = super().populate_user(request, sociallogin, data)
        # No username field to set — email is all we need
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        """Always allow auto signup for social accounts (skip the signup form)."""
        return True
