# Enhanced Rails Project Scanner Test File
# This file contains various Rails security vulnerabilities for testing

class UsersController < ApplicationController
  def create
    # CRITICAL VULNERABILITY: Mass assignment without strong parameters
    @user = User.create(params[:user])
    
    if @user.save
      redirect_to @user
    else
      render :new
    end
  end

  def update
    @user = User.find(params[:id])
    # CRITICAL VULNERABILITY: Direct params usage in update
    @user.update_attributes(params[:user])
    redirect_to @user
  end

  def bulk_create
    # HIGH VULNERABILITY: Bulk operation with unsafe params
    users_data = params[:users]
    users_data.each do |user_data|
      User.create(user_data)
    end
  end

  def search
    # MEDIUM VULNERABILITY: Unsafe find usage
    @user = User.find(params[:id])
    render json: @user
  end

  def admin_update
    # CRITICAL VULNERABILITY: Could allow privilege escalation
    @user = User.find(params[:id])
    @user.update(params.require(:user))  # Still unsafe - no permit!
  end

  private

  def safe_user_params
    # GOOD: This is how it should be done
    params.require(:user).permit(:name, :email, :bio)
  end
end

class TasksController < ApplicationController
  def create
    # CRITICAL: Another mass assignment vulnerability
    @task = current_user.tasks.create(params[:task])
    redirect_to @task
  end

  def update
    @task = current_user.tasks.find(params[:id])
    # CRITICAL: Update with raw params
    if @task.update(params[:task])
      redirect_to @task
    else
      render :edit
    end
  end
  
  def bulk_update
    # PERFORMANCE ISSUE: N+1 problem
    params[:task_ids].each do |task_id|
      task = Task.find(task_id)
      task.save
    end
  end
end

# Rails 4 deprecated patterns
class LegacyController < ApplicationController
  before_filter :authenticate_user!  # DEPRECATED: Use before_action
  after_filter :cleanup              # DEPRECATED: Use after_action
  
  def legacy_update
    @record = Record.find(params[:id])
    @record.update_attributes(params[:record])  # DEPRECATED: Use update
  end
end
