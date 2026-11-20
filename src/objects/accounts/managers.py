from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager[T: AbstractBaseUser](BaseUserManager[T]):
    use_in_migrations = True

    def _create_user(
        self,
        username: str,
        email: str | None,
        password: str | None,
        **extra_fields: object,
    ) -> T:
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: object,
    ) -> T:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str,
        **extra_fields: object,
    ) -> T:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)
