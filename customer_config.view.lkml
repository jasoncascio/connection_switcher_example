view: current_config_state {
  derived_table: {
    sql:
      SELECT
          customer_name
      FROM ${customer_config.SQL_TABLE_NAME}
      WHERE 1=1
      AND database_wh = '{{ _user_attributes['switcher_database_wh']}}'
      AND database_name = '{{ _user_attributes['switcher_database_name']}}'
    ;;
  }

  dimension: current_customer_name {
    type: string
    sql: ${TABLE}.customer_name ;;
  }

  dimension: current_database_name {
    type: string
    sql: '{{ _user_attributes['switcher_database_name']}}' ;;
  }

  dimension: current_database_wh {
    label: "Current Database WH"
    type: string
    sql: '{{ _user_attributes['switcher_database_wh']}}' ;;
  }

  dimension: who_am_i {
    type: string
    sql: '{{ _user_attributes['name']}} (user id: {{ _user_attributes['id'] | round: 0}})' ;;
  }
}


view: customer_config {
  derived_table: {
    sql:
      WITH config AS (
        SELECT NULL AS customer_name, NULL AS database_wh, NULL AS database_name
        UNION ALL SELECT 'Customer 1', 'db_wh_1', 'transactions'
        UNION ALL SELECT 'Customer 2', 'db_wh_2', 'transactions'
        UNION ALL SELECT 'Customer 3', 'db_wh_3', 'transactions'
      )
      SELECT * FROM config WHERE customer_name IS NOT NULL
    ;;
  }

  dimension: customer_name {
    type: string
    sql: ${TABLE}.customer_name ;;
  }

  dimension: database_wh {
    type: string
    sql: ${TABLE}.database_wh ;;
  }

  dimension: database_name {
    type: string
    sql: ${TABLE}.database_name ;;
  }

  dimension: switch_to {
    type: string
    sql:
      CASE
        WHEN ${current_config_state.current_customer_name} = ${customer_name} THEN 'AAA ' || ${customer_name}
        ELSE ${customer_name}
      END
    ;;
    html:
      {% if customer_config.customer_name._value == current_config_state.current_customer_name._value %}
          <span style="font-weight: bold; color: red">--> {{ customer_config.customer_name._rendered_value }} ({{ customer_config.database_wh._rendered_value }}/{{ customer_config.database_name._rendered_value }})</span>
      {% else %}
          <span>Switch to {{ customer_config.customer_name._rendered_value }} ({{ customer_config.database_wh._rendered_value }}/{{ customer_config.database_name._rendered_value }})</span>
      {% endif %}
    ;;
    action: {
      label: "Switch to {{ customer_config.customer_name._rendered_value }} ({{ customer_config.database_wh._rendered_value }}/{{ customer_config.database_name._rendered_value }}"
      url: "https://us-central1-jc-looker.cloudfunctions.net/looker-customer-switcher"
      # form_url: "https://example.com/ping/{{ value }}/form.json"
      # icon_url: "https://looker.com/favicon.ico"
      param: {
        name: "switcher_database_wh" # must match expected field name in cloud function
        value: "{{ customer_config.database_wh._value }}"
      }
      param: {
        name: "switcher_database_name" # must match expected field name in cloud function
        value: "{{ customer_config.database_name._value }}"
      }
      user_attribute_param: { # be sure to set this attribute's value to be hidden and add domain allowlist
        user_attribute: customer_switcher_authentication_secret
        name: "customer_switcher_authentication_secret" # must match expected field name in cloud function
      }
      user_attribute_param: {
        user_attribute: id
        name: "user_id" # must match expected field name in cloud function
      }
    }
  }

}


# label: "Label to Appear in Action Menu"
# url: "https://example.com/posts"
# icon_url: "https://looker.com/favicon.ico"
# form_url: "https://example.com/ping/{{ value }}/form.json"
# param: {
#   name: "name string"
#   value: "value string"
# }
# form_param: {
#   name:  "name string"
#   type: textarea | string | select
#   label:  "possibly-localized-string"
#   option: {
#     name:  "name string"
#     label:  "possibly-localized-string"
#   }
#   required:  yes | no
#   description:  "possibly-localized-string"
#   default:  "string"
# }
# user_attribute_param: {
#   user_attribute: user_attribute_name
#   name: "name_for_json_payload"
# }
