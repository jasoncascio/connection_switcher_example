connection: "jc-looker"

include: "*.view.lkml"                # include all views in the views/ folder in this project

access_grant: can_switch_customer {
  user_attribute: can_switch_customer
  allowed_values: ["Yes"]
   # create a group for users who can switch, add users, give attribute value "Yes"
  # for corresponding group
}





explore: customer_config {
  required_access_grants: [can_switch_customer] #limits who can see this explore

  # access_filter: { could add access filters as necessary to limit customer exposure
  #   user_attribute: allowed_customers
  #   field: customer_config.customer_name
  # }

  query: switcher {
    dimensions: [
      current_config_state.who_am_i,
      current_config_state.current_customer_name,
      current_config_state.current_database_wh,
      current_config_state.current_database_name,
      switch_to
    ]
    label: "Customer Switcher"
    description: "Shows the current customer and allows you to switch to others"
    sorts: [customer_config.switch_to: asc]
  }

  join: current_config_state {
    type: cross
    relationship: many_to_one
  }
}
