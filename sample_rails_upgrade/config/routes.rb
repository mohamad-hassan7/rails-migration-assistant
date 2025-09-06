Rails.application.routes.draw do
  # Legacy routing patterns that need migration assistance
  
  # Deprecated route syntax (Rails 3 style)
  match '/users/:id' => 'users#show'
  match '/admin' => 'admin#index', :via => :get
  
  # Legacy resource routing with deprecated options
  resources :posts do
    # Deprecated member and collection syntax
    member do
      get :preview
      put :publish
    end
    
    collection do
      get :archived
    end
    
    # Nested resources with legacy patterns
    resources :comments, :except => [:destroy] do
      member do
        post :approve
        delete :spam
      end
    end
  end
  
  # Legacy named routes with deprecated syntax
  match '/login' => 'sessions#new', :as => :login, :via => :get
  match '/logout' => 'sessions#destroy', :as => :logout, :via => :delete
  match '/signup' => 'users#new', :as => :signup, :via => :get
  
  # Deprecated namespace syntax
  namespace :admin do
    resources :users do
      member { put :activate }
      member { put :deactivate }
    end
    
    resources :settings, :only => [:index, :update]
  end
  
  # Legacy scope routing
  scope :path => '/api', :module => 'api' do
    scope :path => '/v1', :module => 'v1' do
      resources :articles, :defaults => { :format => 'json' }
    end
  end
  
  # Deprecated constraints syntax
  constraints(:subdomain => 'api') do
    namespace :api, :path => '/' do
      resources :widgets
    end
  end
  
  # Legacy root route
  match '/' => 'home#index', :via => :get
  
  # Deprecated catch-all route (security issue)
  match '*path' => 'application#routing_error', :via => :all
  
  # Legacy format constraints
  resources :documents, :constraints => { :format => /(pdf|doc|docx)/ }
  
  # Deprecated route globbing
  match '/files/*path' => 'files#show', :via => :get
  
  # Legacy route with lambda constraints
  resources :events, :constraints => lambda { |req| 
    req.subdomain.present? && req.subdomain != 'www' 
  }
  
  # Deprecated route priorities (should be at top)
  match '/special' => 'special#index', :via => :get
  
  # Legacy mobile routing patterns
  constraints :mobile => true do
    match '/mobile' => 'mobile#index', :via => :get
  end
  
  # Deprecated direct route definitions
  get '/health_check', :to => proc { |env| [200, {}, ['OK']] }
end
