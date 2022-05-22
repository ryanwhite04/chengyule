from click import argument, option

class Cli:
    
    def init_app(self, app, db):

        from app.models import User

        @app.cli.group()
        def admin():
            """User Management"""
            pass

        @admin.command()
        @argument("username")
        @option("--role", "-r", default=None, show_default=True)
        def update(username, role):
            """
            Update users
            Roles:
                0: admin (has access to database)
            """
            roles = ["admin", "editor"]
            user = User.query.where(User.username == username).first()
            try:
                user.role = roles[int(role)] if role else None
                db.session.add(user)
                db.session.commit()
            except IndexError as e:
                print("That role doesn't exist")
                print(f"Roles include:")
                for i, role in enumerate(roles):
                    print(f"{i}: {role}")
                db.session.rollback()
            print(User.query.get(user.id))