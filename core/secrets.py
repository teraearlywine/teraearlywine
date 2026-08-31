import os


def load_secret(setting_name, logger):
    """Load a secret from the environment or Google Secret Manager."""
    direct_value = os.environ.get(setting_name, '').strip()
    if direct_value:
        return direct_value

    secret_id = os.environ.get(f'{setting_name}_SECRET_ID', '').strip()
    if not secret_id:
        return ''

    project_id = (
        os.environ.get('GOOGLE_CLOUD_PROJECT', '').strip()
        or os.environ.get('GCP_PROJECT', '').strip()
    )
    if not project_id and not secret_id.startswith('projects/'):
        logger.error(
            '%s_SECRET_ID is configured, but no Google Cloud project is available',
            setting_name,
        )
        return ''

    resource_name = secret_id
    if not secret_id.startswith('projects/'):
        resource_name = (
            f'projects/{project_id}/secrets/{secret_id}/versions/latest'
        )
    elif '/versions/' not in secret_id:
        resource_name = f'{secret_id}/versions/latest'

    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(
            request={'name': resource_name},
        )
        return response.payload.data.decode('utf-8').strip()
    except Exception:
        logger.exception(
            'Unable to load %s from Google Secret Manager',
            setting_name,
        )
        return ''
