
cd /opt/odoo13
rm -rf odoo-custom-addons.zip
rm -rf odoo-custom-addons
wget https://hq.vegaforce.com.tw/download/odoo/odoo-custom-addons.zip
unzip odoo-custom-addons.zip
ls -lha
mv odoo-custom-addons-mockup/ odoo-custom-addons
chmod 777 -R odoo-custom-addons/
systemctl restart odoo13
systemctl status odoo13


class AcsConfigSettings(models.TransientModel):
    _name = 'acs.config.settings'
    _inherit = 'res.config.settings'
    
    deviceserver = fields.Char(string='卡機伺服器網址')

    def _onchange_deviceserver(self):
        if not self.deviceserver:
            self.deviceserver = "http://odooerp.morespace.com.tw:9090"

    def get_values(self):
        res = super(AcsConfigSettings, self).get_values()
        res.update(
            deviceserver=self.env['ir.config_parameter'].sudo().get_param('acs.deviceserver')
        )
        return res

    def set_values(self):
        super(AcsConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('acs.deviceserver', self.deviceserver)

#class AcsCardOwner(models.Model):
#    _name = 'acs.cardowner'
#    _description = '卡片所有人'
#    _inherit = 'res.partner'

#    @api.model
#    def name_search(self, name='', args=None, operator='ilike', limit=100):
#        if self._context.get('search_by_vat', False):
#            if name:
#                args = args if args else []
#                args.extend(['|', ['name', 'ilike', name], ['vat', 'ilike', name]])
#                name = ''
#        return super(AcsCardOwner, self).name_search(name=name, args=args, operator=operator, limit=limit)


    #修改卡片顯示名稱
    # def name_get(self, cr, uid, ids, context=None):
    #     if not len(ids):
    #         return []
    #     res = [(r['id'], r['name'] and '%s [%s]' % (r['name'], r['name2']) or r['name'] ) for r in self.read(cr, uid, ids, ['name', 'name2'], context=context) ]
    #     return res

    # def search_filtered_locker(self):
    #     self.ensure_one()
    #     return {           
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'asc.locker',
    #         'type': 'ir.actions.act_window',
    #         'domain':[('contract_id', '=', '' )],
    #     }
<tree string="聯繫人" modifiers="{}">
	<field name="display_name" string="名稱" modifiers="{'readonly':true}"/>
	<field name="function" invisible="1" modifiers="{'column_invisible':true}"/>
	<field name="phone" class="o_force_ltr" optional="show" on_change="1" modifiers="{}"/>
	<field name="email" optional="show" on_change="1" modifiers="{}"/>
	<field name="company_id" on_change="1" can_create="true" can_write="true" invisible="1" modifiers="{'invisible':true,'column_invisible':true}"/>
	<field name="city" optional="hide" modifiers="{}"/>
	<field name="state_id" optional="hide" on_change="1" can_create="true" can_write="true" modifiers="{}"/>
	<field name="country_id" optional="hide" on_change="1" can_create="true" can_write="true" modifiers="{}"/>
	<field name="vat" optional="hide" modifiers="{}"/>
	<field name="user_id" invisible="1" can_create="true" can_write="true" modifiers="{'column_invisible':true}"/>
	<field name="is_company" invisible="1" on_change="1" modifiers="{'column_invisible':true}"/>
	<field name="parent_id" invisible="1" on_change="1" can_create="true" can_write="true" modifiers="{'column_invisible':true}"/>
	<field name="active" invisible="1" modifiers="{'column_invisible':true}"/>
</tree>
<tree string="Contacts">
    <field name="display_name" string="Name"/>
    <field name="function" invisible="1"/>
    <field name="phone" class="o_force_ltr" optional="show"/>
    <field name="email" optional="show"/>
    <field name="company_id" groups="base.group_multi_company"/>
    <field name="city" optional="hide"/>
    <field name="state_id" optional="hide"/>
    <field name="country_id" optional="hide"/>
    <field name="vat" optional="hide"/>
    <field name="user_id" invisible="1"/>
    <field name="is_company" invisible="1"/>
    <field name="parent_id" invisible="1"/>
    <field name="active" invisible="1"/>
</tree>

<tree string="Employees">
    <field name="name"/>
    <field name="work_phone" class="o_force_ltr"/>
    <field name="work_email"/>
    <field name="company_id" groups="base.group_multi_company"/>
    <field name="department_id"/>
    <field name="job_id"/>
    <field name="parent_id"/>
    <field name="coach_id" invisible="1"/>
</tree>
檢視名稱 hr.employee.search
檢視類型 搜尋
外部 ID	hr.view_employee_filter
<search string="Employees">
    <field name="name" string="Employee" filter_domain="['|', ('work_email', 'ilike', self), ('name', 'ilike', self)]"/>
    <field name="category_ids" groups="hr.group_hr_user"/>
    <field name="job_id"/>
    <separator/>
    <filter string="Unread Messages" name="message_needaction" domain="[('message_needaction', '=', True)]"/>
    <separator/>
    <filter invisible="1" string="Late Activities" name="activities_overdue" domain="[('activity_ids.date_deadline', '&lt;', context_today().strftime('%Y-%m-%d'))]"/>
    <filter invisible="1" string="Today Activities" name="activities_today" domain="[('activity_ids.date_deadline', '=', context_today().strftime('%Y-%m-%d'))]"/>
    <filter invisible="1" string="Future Activities" name="activities_upcoming_all" domain="[('activity_ids.date_deadline', '&gt;', context_today().strftime('%Y-%m-%d'))]"/>
    <separator/>
    <filter string="Archived" name="inactive" domain="[('active', '=', False)]"/>
    <group expand="0" string="Group By">
        <filter name="group_manager" string="Manager" domain="[]" context="{'group_by': 'parent_id'}"/>
        <filter name="group_department" string="Department" domain="[]" context="{'group_by': 'department_id'}"/>
        <filter name="group_job" string="Job" domain="[]" context="{'group_by': 'job_id'}"/>
    </group>
    <searchpanel>
        <field name="company_id" groups="base.group_multi_company" icon="fa-building"/>
        <field name="department_id" icon="fa-users"/>
    </searchpanel>
</search>

<kanban class="o_hr_employee_kanban">
    <field name="id"/>
    <field name="hr_presence_state"/>
    <templates>
        <t t-name="kanban-box">
        <div class="oe_kanban_global_click o_kanban_record_has_image_fill o_hr_kanban_record">
            <field name="image_128" widget="image" class="o_kanban_image_fill_left" options="{'zoom': true, 'zoom_delay': 1000, 'background': true, 'preventClicks': false}"/>

            <div class="oe_kanban_details">
                <div class="o_kanban_record_top">
                    <div class="o_kanban_record_headings">
                        <strong class="o_kanban_record_title">
                            <div class="float-right" t-if="record.hr_presence_state.raw_value == 'present'">
                                <span class="fa fa-circle text-success" role="img" aria-label="Present" title="Present" name="presence_present"/>
                            </div>
                            <div class="float-right" t-if="record.hr_presence_state.raw_value == 'absent'">
                                <span class="fa fa-circle text-danger" role="img" aria-label="Absent" title="Absent" name="presence_absent"/>
                            </div>
                            <div class="float-right" t-if="record.hr_presence_state.raw_value == 'to_define'">
                                <span class="fa fa-circle text-warning" role="img" aria-label="To define" title="To define" name="presence_to_define"/>
                            </div>
                            <field name="name" placeholder="Employee's Name"/>
                        </strong>
                        <span t-if="record.job_title.raw_value" class="o_kanban_record_subtitle"><field name="job_title"/></span>
                    </div>
                </div>
                <field name="category_ids" widget="many2many_tags" options="{'color_field': 'color'}" groups="hr.group_hr_manager"/>
                <ul>
                    <li id="last_login"/>
                    <li t-if="record.work_email.raw_value" class="o_text_overflow"><field name="work_email"/></li>
                    <li t-if="record.work_phone.raw_value" class="o_force_ltr"><field name="work_phone"/></li>
                </ul>
            </div>
        </div>
        </t>
    </templates>
</kanban>
