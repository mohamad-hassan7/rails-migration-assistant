# Environment configuration for development
# Contains legacy patterns that need migration assistance

Rails.application.configure do
  # Legacy development configuration
  config.cache_classes = false
  
  # Deprecated eager loading configuration
  config.eager_load = false
  
  # Legacy asset configuration (pre-Webpacker)
  config.assets.debug = true
  config.assets.quiet = true
  config.assets.compile = true
  config.assets.digest = false
  
  # Deprecated asset pipeline configuration
  config.serve_static_assets = true
  config.static_cache_control = "public, max-age=3600"
  
  # Legacy Active Record configuration
  config.active_record.migration_error = :page_load
  config.active_record.verbose_query_logs = true
  config.active_record.raise_in_transactional_callbacks = true
  
  # Deprecated mailer configuration
  config.action_mailer.raise_delivery_errors = true
  config.action_mailer.delivery_method = :smtp
  config.action_mailer.smtp_settings = {
    address: "localhost",
    port: 1025,
    authentication: :plain,
    enable_starttls_auto: false
  }
  config.action_mailer.default_url_options = { host: 'localhost:3000' }
  config.action_mailer.asset_host = 'http://localhost:3000'
  
  # Legacy view configuration
  config.action_view.raise_on_missing_translations = true
  config.action_view.debug_missing_translation = true
  
  # Deprecated controller configuration
  config.action_controller.perform_caching = true
  config.action_controller.enable_fragment_cache_logging = true
  config.action_controller.action_on_unpermitted_parameters = :log
  
  # Legacy caching configuration
  config.cache_store = :memory_store, { size: 64.megabytes }
  config.public_file_server.headers = {
    'Cache-Control' => 'public, max-age=3600'
  }
  
  # Deprecated Active Job configuration
  config.active_job.queue_adapter = :inline
  config.active_job.verbose_enqueue_logs = true
  
  # Legacy logging configuration
  config.log_level = :debug
  config.log_tags = [ :request_id ]
  config.logger = ActiveSupport::Logger.new(STDOUT)
  config.colorize_logging = true
  
  # Deprecated middleware configuration
  config.middleware.use "Rack::LiveReload"
  config.middleware.delete "Rack::Lock"
  
  # Legacy security configuration
  config.force_ssl = false
  config.ssl_options = { redirect: { exclude: -> request { request.path =~ /health/ } } }
  
  # Deprecated file watching configuration
  config.file_watcher = ActiveSupport::EventedFileUpdateChecker
  config.reload_classes_only_on_change = false
  
  # Legacy I18n configuration
  config.i18n.fallbacks = false
  config.i18n.raise_on_missing_translations = false
  
  # Deprecated timezone configuration
  config.time_zone = 'Eastern Time (US & Canada)'
  config.beginning_of_week = :monday
  
  # Legacy exception handling
  config.consider_all_requests_local = true
  config.action_dispatch.show_exceptions = true
  
  # Deprecated generator configuration
  config.generators.system_tests = nil
  config.generators.assets = false
  config.generators.helper = false
  
  # Legacy autoloading configuration (Zeitwerk compatibility issues)
  config.autoloader = :classic
  config.enable_dependency_loading = true
  config.autoload_paths += Dir[Rails.root.join("app", "models", "{*/}")]
  
  # Deprecated Active Storage configuration
  config.active_storage.variant_processor = :mini_magick
  config.active_storage.queue = :default
  
  # Legacy session configuration
  config.session_store :cookie_store, 
    key: '_sample_app_session',
    secure: false,
    httponly: false,
    expire_after: 1.year
    
  # Deprecated CORS configuration
  config.middleware.insert_before 0, Rack::Cors do
    allow do
      origins 'localhost:3000', '127.0.0.1:3000'
      resource '*',
        headers: :any,
        methods: [:get, :post, :put, :patch, :delete, :options, :head],
        credentials: true
    end
  end
end
