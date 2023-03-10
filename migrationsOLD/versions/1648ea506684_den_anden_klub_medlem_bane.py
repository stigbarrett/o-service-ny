"""den anden klub, medlem, bane

Revision ID: 1648ea506684
Revises: 
Create Date: 2022-05-20 11:52:54.183795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1648ea506684'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('klub',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('langtnavn', sa.String(length=80), nullable=True),
    sa.Column('kortnavn', sa.String(length=40), nullable=True),
    sa.Column('tom', sa.String(length=10), nullable=True),
    sa.Column('kreds', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('konkurrence_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('konkurrence', sa.String(length=80), nullable=True),
    sa.Column('arrangerendeKlub', sa.String(length=120), nullable=True),
    sa.Column('konkurrenceDato', sa.Date(), nullable=True),
    sa.Column('konkurrenceType', sa.String(length=80), nullable=True),
    sa.Column('ansvarligNavn', sa.String(length=80), nullable=True),
    sa.Column('dataFormat', sa.String(length=20), nullable=True),
    sa.Column('ViKaSki_point', sa.String(length=20), nullable=True),
    sa.Column('pathKonkurrenceFiler', sa.String(length=80), nullable=True),
    sa.Column('filNavn', sa.String(length=80), nullable=True),
    sa.Column('otracklink', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_konkurrence_data_timestamp'), 'konkurrence_data', ['timestamp'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.Column('last_message_read_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('medlemmer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('navn', sa.String(length=80), nullable=True),
    sa.Column('navn_ok', sa.Integer(), nullable=True),
    sa.Column('emitbrik', sa.Integer(), nullable=True),
    sa.Column('samlet_point', sa.Integer(), nullable=True),
    sa.Column('klub_id', sa.Integer(), nullable=True),
    sa.Column('Kon', sa.String(length=20), nullable=True),
    sa.Column('Egen_brik', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['klub_id'], ['klub.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_timestamp'), 'message', ['timestamp'], unique=False)
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.Column('payload_json', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_name'), 'notification', ['name'], unique=False)
    op.create_index(op.f('ix_notification_timestamp'), 'notification', ['timestamp'], unique=False)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(length=5), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('task',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('complete', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_name'), 'task', ['name'], unique=False)
    op.create_table('baneresultat',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('navn', sa.String(length=80), nullable=True),
    sa.Column('klub', sa.String(length=120), nullable=True),
    sa.Column('bane', sa.String(length=80), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('tid', sa.String(length=30), nullable=True),
    sa.Column('placering', sa.Integer(), nullable=True),
    sa.Column('point', sa.String(length=10), nullable=True),
    sa.Column('tidsek', sa.Integer(), nullable=True),
    sa.Column('medlemmer_id', sa.Integer(), nullable=True),
    sa.Column('konkurrenceId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['konkurrenceId'], ['konkurrence_data.id'], ),
    sa.ForeignKeyConstraint(['medlemmer_id'], ['medlemmer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_baneresultat_medlemmer_id'), 'baneresultat', ['medlemmer_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_baneresultat_medlemmer_id'), table_name='baneresultat')
    op.drop_table('baneresultat')
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_table('task')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_notification_timestamp'), table_name='notification')
    op.drop_index(op.f('ix_notification_name'), table_name='notification')
    op.drop_table('notification')
    op.drop_index(op.f('ix_message_timestamp'), table_name='message')
    op.drop_table('message')
    op.drop_table('medlemmer')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_konkurrence_data_timestamp'), table_name='konkurrence_data')
    op.drop_table('konkurrence_data')
    op.drop_table('klub')
    # ### end Alembic commands ###
