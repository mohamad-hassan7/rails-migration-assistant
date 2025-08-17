class ApplicationController < ActionController::Base
  # Deprecated patterns for testing
  before_filter :authenticate_user!
  after_filter :track_action
  skip_before_filter :verify_authenticity_token, only: [:api_endpoint]
  
  protect_from_forgery with: :exception
  
  private
  
  def authenticate_user!
    # Authentication logic
    redirect_to login_path unless current_user
  end
  
  def track_action
    # Tracking logic
  end
  
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
  
  # Unsafe parameter usage - security issue
  def create_user
    user = User.create(params[:user])  # Missing strong parameters
    render json: user
  end
  
  # Performance issue - N+1 query
  def list_posts
    @posts = Post.all
    @posts.each do |post|
      post.comments.count  # This will cause N+1 queries
    end
  end
end
