"""Initial migration

Revision ID: 31286bfe2a93
Revises: 
Create Date: 2024-12-05 21:22:15.590890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31286bfe2a93'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unique_id', sa.String(), nullable=False),
    sa.Column('favorite', sa.Boolean(), nullable=True),
    sa.Column('status_module', sa.Integer(), nullable=True),
    sa.Column('status_friendlyname', sa.String(), nullable=True),
    sa.Column('status_topic', sa.String(), nullable=True),
    sa.Column('status_buttontopic', sa.String(), nullable=True),
    sa.Column('status_power', sa.Integer(), nullable=True),
    sa.Column('status_poweronstate', sa.Integer(), nullable=True),
    sa.Column('status_ledstate', sa.Integer(), nullable=True),
    sa.Column('status_savedata', sa.Integer(), nullable=True),
    sa.Column('status_savestate', sa.Integer(), nullable=True),
    sa.Column('status_buttonretain', sa.Integer(), nullable=True),
    sa.Column('status_powerretain', sa.Integer(), nullable=True),
    sa.Column('statusprm_baudrate', sa.Integer(), nullable=True),
    sa.Column('statusprm_grouptopic', sa.String(), nullable=True),
    sa.Column('statusprm_oturl', sa.String(), nullable=True),
    sa.Column('statusprm_uptime', sa.String(), nullable=True),
    sa.Column('statusprm_sleep', sa.Integer(), nullable=True),
    sa.Column('statusprm_bootcount', sa.Integer(), nullable=True),
    sa.Column('statusprm_savecount', sa.Integer(), nullable=True),
    sa.Column('statusprm_saveaddress', sa.String(), nullable=True),
    sa.Column('statusfwr_version', sa.String(), nullable=True),
    sa.Column('statusfwr_builddatetime', sa.String(), nullable=True),
    sa.Column('statusfwr_boot', sa.Integer(), nullable=True),
    sa.Column('statusfwr_core', sa.String(), nullable=True),
    sa.Column('statusfwr_sdk', sa.String(), nullable=True),
    sa.Column('statuslog_seriallog', sa.Integer(), nullable=True),
    sa.Column('statuslog_weblog', sa.Integer(), nullable=True),
    sa.Column('statuslog_syslog', sa.Integer(), nullable=True),
    sa.Column('statuslog_loghost', sa.String(), nullable=True),
    sa.Column('statuslog_logport', sa.Integer(), nullable=True),
    sa.Column('statuslog_ssid1', sa.String(), nullable=True),
    sa.Column('statuslog_ssid2', sa.String(), nullable=True),
    sa.Column('statuslog_teleperiod', sa.Integer(), nullable=True),
    sa.Column('statuslog_setoption', sa.String(), nullable=True),
    sa.Column('statusmem_programsize', sa.Integer(), nullable=True),
    sa.Column('statusmem_free', sa.Integer(), nullable=True),
    sa.Column('statusmem_heap', sa.Integer(), nullable=True),
    sa.Column('statusmem_programflashsize', sa.Integer(), nullable=True),
    sa.Column('statusmem_flashsize', sa.Integer(), nullable=True),
    sa.Column('statusmem_flashmode', sa.Integer(), nullable=True),
    sa.Column('statusnet_hostname', sa.String(), nullable=True),
    sa.Column('statusnet_ipaddress', sa.String(), nullable=True),
    sa.Column('statusnet_gateway', sa.String(), nullable=True),
    sa.Column('statusnet_subnetmask', sa.String(), nullable=True),
    sa.Column('statusnet_dnssserver', sa.String(), nullable=True),
    sa.Column('statusnet_mac', sa.String(), nullable=True),
    sa.Column('statusnet_webserver', sa.Integer(), nullable=True),
    sa.Column('statusnet_wificonfig', sa.Integer(), nullable=True),
    sa.Column('statustim_utc', sa.String(), nullable=True),
    sa.Column('statustim_local', sa.String(), nullable=True),
    sa.Column('statustim_startdst', sa.String(), nullable=True),
    sa.Column('statustim_enddst', sa.String(), nullable=True),
    sa.Column('statustim_timezone', sa.Integer(), nullable=True),
    sa.Column('statussns_time', sa.String(), nullable=True),
    sa.Column('statussns_switch1', sa.String(), nullable=True),
    sa.Column('statussts_time', sa.String(), nullable=True),
    sa.Column('statussts_uptime', sa.String(), nullable=True),
    sa.Column('statussts_vcc', sa.Float(), nullable=True),
    sa.Column('statussts_power', sa.String(), nullable=True),
    sa.Column('statussts_wifi_ap', sa.Integer(), nullable=True),
    sa.Column('statussts_wifi_ssid', sa.String(), nullable=True),
    sa.Column('statussts_wifi_rssi', sa.Integer(), nullable=True),
    sa.Column('statussts_wifi_apmac', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('unique_id')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')
    # ### end Alembic commands ###
