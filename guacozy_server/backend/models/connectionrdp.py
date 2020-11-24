from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

from backend.common.dictionaries import RDPSecurityDict
from backend.common.utils import model_choices_from_dictionary
from .connection import Connection
from .credentials import Credentials, StaticCredentials, NamedCredentials, PersonalNamedCredentials


class ConnectionRdp(Connection):
    class Meta:
        verbose_name = "RDP Connection"
        verbose_name_plural = "RDP Connections"

    # Guacamole connectin settings are explained here:
    # https://guacamole.apache.org/doc/gug/configuring-guacamole.html#rdp

    # Security
    ignore_cert = models.BooleanField(blank=False, default=False)
    security = models.CharField(
        max_length=10,
        choices=model_choices_from_dictionary(RDPSecurityDict),
        default='any'
    )
    disable_auth = models.BooleanField(blank=False, default=False)

    # Session settings
    console = models.BooleanField(blank=False, default=False)
    initial_program = models.CharField(max_length=255, blank=True, null=True)
    server_layout = models.CharField(max_length=12,
                                     blank=False,
                                     choices=[
                                         ('en-us-qwerty',
                                          'English (US) keyboard'),
                                         ('en-gb-qwerty',
                                          'English (UK) keyboard'),
                                         ('de-de-qwertz',
                                          'German keyboard (qwertz)'),
                                         ('fr-fr-azerty',
                                          'French keyboard (azerty)'),
                                         ('fr-ch-qwertz',
                                          'Swiss French keyboard (qwertz)'),
                                         ('it-it-qwerty',
                                          'Italian keyboard'),
                                         ('ja-jp-qwerty',
                                          'Japanese keyboard'),
                                         ('pt-br-qwerty',
                                          'Portuguese Brazilian keyboard'),
                                         ('es-es-qwerty',
                                          'Spanish keyboard'),
                                         ('sv-se-qwerty',
                                          'Swedish keyboard'),
                                         ('tr-tr-qwerty',
                                          'Turkish-Q keyboard'),
                                         ('failsafe', 'Failsafe')
                                     ],
                                     default='en-us-qwerty')

    # Gateway settings
    gateway_hostname = models.CharField(max_length=60, blank=True, null=True)
    gateway_port = models.IntegerField(null=True, blank=True)
    gateway_credentials = models.ForeignKey(Credentials,
                                    verbose_name="Gateway Credentials",
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    gateway_username = models.CharField(
        verbose_name="Gateway Username",
        max_length=50,
        blank=True,
        null=True)
    gateway_password = EncryptedCharField(
        verbose_name="Gateway Password",
        max_length=50,
        blank=True,
        null=True)
    gateway_domain = models.CharField(
        verbose_name="Gateway Domain",
        max_length=50,
        blank=True,
        null=True)


    # Display settings
    color_depth = models.CharField(max_length=2,
                                   choices=[
                                       ('8', '8 bits'),
                                       ('16', '16 bits'),
                                       ('24', '24 bits'),
                                   ],
                                   default='16')

    resize_method = models.CharField(max_length=20,
                                     choices=[
                                         ('reconnect', 'Reconnect'),
                                         ('display-update', 'Display Update')
                                     ],
                                     default='reconnect')

    # RemoteApp settings
    remote_app = models.CharField(max_length=255, blank=True, null=True)
    remote_app_working_dir = models.CharField(max_length=300, blank=True, null=True)
    remote_app_args = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.protocol = 'rdp'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + " (RDP)"

    # Update Guacamole connection parameters with RDP specific parameters
    def get_guacamole_parameters(self, user):
        parameters = super().get_guacamole_parameters(user=user)

        if not self.port:
            parameters["port"] = 3389

        # Network settings
        parameters["ignore_cert"] = self.ignore_cert.__str__().lower()
        parameters["security"] = self.security
        parameters["disable_auth"] = self.disable_auth.__str__().lower()

        # Session settings
        parameters["console"] = self.console.__str__().lower()
        parameters["initial_program"] = self.initial_program
        parameters["server_layout"] = self.server_layout

        # Gateway settings
        if self.gateway_hostname:
            parameters["gateway-hostname"] = self.gateway_hostname
            if self.gateway_port:
                parameters["gateway-port"] = self.gateway_port
            else:
                parameters["gateway-port"] = 443

            gateway_credentials_object = \
                self.get_gateway_credentials_object(user)

            if gateway_credentials_object is not None:
                parameters["gateway-username"] = gateway_credentials_object.username \
                    if gateway_credentials_object.username else ""
                parameters["gateway-password"] = gateway_credentials_object.password \
                    if gateway_credentials_object.password else ""
                parameters["gateway-domain"] = gateway_credentials_object.domain \
                    if gateway_credentials_object.domain else ""
            else:
                parameters["gateway-username"] = self.gateway_username \
                    if self.gateway_username else ""
                parameters["gateway-password"] = self.gateway_password \
                    if self.gateway_password else ""
                parameters["gateway-domain"] = self.gateway_domain \
                    if self.gateway_domain else ""
            

        # Display settings
        parameters["color_depth"] = self.color_depth
        parameters["resize_method"] = self.resize_method

        # RemoteApp settings
        if self.remote_app:
            parameters["remote-app"] = self.remote_app
            parameters["remote-app-dir"] = self.remote_app_working_dir
            parameters["remote-app-args"] = self.remote_app_args

        return parameters

    def get_gateway_credentials_object(self, user):
        if self.gateway_credentials is None:
          return None

        try:
            # Check if credentials is StaticCredentials. Return if it is
            static_credentials = StaticCredentials.objects.get(pk=self.gateway_credentials.pk)
            return static_credentials
        except ObjectDoesNotExist:
            pass

        try:
            # Then check if this is a NamedCredentials
            named_credentials = NamedCredentials.objects.get(pk=self.gateway_credentials.pk)
            # If it is NamedCredentials, we need user-specific instance
            named_credentials_instance = PersonalNamedCredentials.objects.get(reference=named_credentials,
                                                                              owner=user)
            return named_credentials_instance
        except (NamedCredentials.DoesNotExist, PersonalNamedCredentials.DoesNotExist):
            pass

        return None
