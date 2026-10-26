from django.db import migrations

def enable_rls_on_postgresql(apps, schema_editor):
    """
    Requirement 1: Enable and force Row Level Security on visitor tables.
    Runs strictly when database vendor is postgresql (Neon).
    """
    connection = schema_editor.connection
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            # Enable RLS on inquiries
            cursor.execute("ALTER TABLE leads_inquiry ENABLE ROW LEVEL SECURITY;")
            cursor.execute("ALTER TABLE leads_inquiry FORCE ROW LEVEL SECURITY;")
            
            # Policy: inserts allowed for app role
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_policies WHERE tablename = 'leads_inquiry' AND policyname = 'inquiry_insert_policy'
                    ) THEN
                        CREATE POLICY inquiry_insert_policy ON leads_inquiry FOR INSERT WITH CHECK (true);
                    END IF;
                END
                $$;
            """)

            # Policy: read/update only for staff
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_policies WHERE tablename = 'leads_inquiry' AND policyname = 'inquiry_staff_policy'
                    ) THEN
                        CREATE POLICY inquiry_staff_policy ON leads_inquiry FOR ALL USING (
                            current_setting('app.is_staff', true) = 'true'
                        );
                    END IF;
                END
                $$;
            """)


def disable_rls_on_postgresql(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE leads_inquiry DISABLE ROW LEVEL SECURITY;")


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0001_initial'),
        ('security_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(enable_rls_on_postgresql, reverse_code=disable_rls_on_postgresql),
    ]
