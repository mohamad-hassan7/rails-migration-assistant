require_relative 'boot'

require 'rails/all'

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module SampleRailsUpgrade
  class Application < Rails::Application
    # Configuration for the application, engines, and railties goes here.
    #
    # These settings can be overridden in specific environments using the files
    # in config/environments/, which are processed later.

    # Legacy configuration patterns that need migration
    config.load_defaults 5.2

    # Deprecated configuration options
    config.active_record.raise_in_transactional_callbacks = true
    config.active_record.belongs_to_required_by_default = false
    
    # Legacy asset pipeline configuration
    config.assets.enabled = true
    config.assets.version = '1.0'
    config.assets.compile = false
    config.assets.digest = true
    
    # Deprecated autoloading configuration
    config.autoload_paths += %W(#{config.root}/lib)
    config.autoload_paths += Dir["#{config.root}/app/models/**/"]
    
    # Legacy middleware configuration
    config.middleware.delete "Rack::Lock"
    config.middleware.use "PDFKit::Middleware"
    
    # Deprecated generators configuration
    config.generators do |g|
      g.orm             :active_record
      g.template_engine :erb
      g.test_framework  :test_unit, fixture: false
      g.stylesheets     false
      g.javascripts     false
    end
    
    # Legacy security configuration
    config.force_ssl = false
    config.ssl_options = { hsts: false }
    
    # Deprecated time zone configuration
    config.time_zone = 'Eastern Time (US & Canada)'
    config.active_record.default_timezone = :local
    
    # Legacy cache configuration
    config.cache_store = :memory_store
    config.action_controller.perform_caching = false
    
    # Deprecated mailer configuration
    config.action_mailer.raise_delivery_errors = false
    config.action_mailer.delivery_method = :sendmail
    
    # Legacy encoding configuration
    config.encoding = "utf-8"
    
    # Deprecated filter parameters
    config.filter_parameters += [:password, :password_confirmation]
    
    # Legacy session configuration
    config.session_store :cookie_store, key: '_sample_rails_upgrade_session'
    
    # Deprecated asset host configuration
    config.action_controller.asset_host = "http://assets.example.com"
    
    # Legacy eager loading configuration
    config.eager_load_paths << Rails.root.join("lib")
    
    # Deprecated Active Job configuration
    config.active_job.queue_adapter = :inline
    
    # Legacy CORS configuration
    config.middleware.insert_before 0, "Rack::Cors" do
      allow do
        origins '*'
        resource '*', headers: :any, methods: [:get, :post, :options]
      end
    end
  end
end
