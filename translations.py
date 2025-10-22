"""
Multi-language support for FarmTwin 360
Currently supports English and Spanish
"""

import streamlit as st

# Translation dictionaries
translations = {
    "en": {
        # Authentication
        "login_title": "FarmTwin 360 - Login",
        "demo_users": "Demo Users",
        "email": "Email",
        "password": "Password",
        "login": "Login",
        "logout": "Logout",
        "login_success": "Login successful!",
        "login_error": "Invalid email or password",
        "welcome": "Welcome",
        "role": "Role",
        
        # Navigation
        "navigation": "Navigation",
        "dashboard": "Dashboard",
        "admin_panel": "Admin Panel",
        "worker_interface": "Worker Interface",
        "visitor_check_in": "Visitor Check-in",
        "analytics": "Analytics",
        
        # Dashboard
        "total_barns": "Total Barns",
        "high_risk_barns": "High Risk Barns",
        "total_checklists": "Total Checklists",
        "unresolved_incidents": "Unresolved Incidents",
        "farm_visualization": "Farm Visualization",
        "recent_activities": "Recent Activities",
        "risk_distribution": "Risk Distribution",
        "checklist_trends": "Checklist Trends",
        "update_ai_predictions": "Update AI Predictions",
        "updating_predictions": "Updating AI predictions...",
        "predictions_updated": "AI predictions updated successfully!",
        "predictions_error": "Error updating predictions",
        
        # Admin Panel
        "user_management": "User Management",
        "farm_management": "Farm Management",
        "system_settings": "System Settings",
        "add_new_user": "Add New User",
        "existing_users": "Existing Users",
        "user_actions": "User Actions",
        "deactivate_user": "Deactivate User",
        "activate_user": "Activate User",
        "deactivate": "Deactivate",
        "activate": "Activate",
        "user_deactivated": "User deactivated successfully",
        "user_activated": "User activated successfully",
        "no_users_found": "No users found",
        "name": "Name",
        "create_user": "Create User",
        "fill_all_fields": "Please fill all required fields",
        "invalid_email": "Invalid email format",
        "add_new_farm": "Add New Farm",
        "existing_farms": "Existing Farms",
        "farm_name": "Farm Name",
        "location": "Location",
        "description": "Description",
        "create_farm": "Create Farm",
        "farm_name_required": "Farm name is required",
        "farm_created": "Farm created successfully",
        "farm_creation_error": "Error creating farm",
        "no_farms_found": "No farms found",
        
        # Worker Interface
        "submit_checklist": "Submit Checklist",
        "report_incident": "Report Incident",
        "my_submissions": "My Submissions",
        "daily_checklist": "Daily Checklist",
        "select_barn": "Select Barn",
        "no_barns_available": "No barns available",
        "hygiene_score": "Hygiene Score (1-10)",
        "mortality_count": "Mortality Count",
        "feed_quality": "Feed Quality (1-10)",
        "water_quality": "Water Quality (1-10)",
        "ventilation_score": "Ventilation Score (1-10)",
        "temperature_celsius": "Temperature (°C)",
        "humidity_percentage": "Humidity (%)",
        "location_data": "Location Data",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "notes": "Notes",
        "upload_photo": "Upload Photo",
        "submit_checklist": "Submit Checklist",
        "incident_report": "Incident Report",
        "incident_type": "Incident Type",
        "severity": "Severity",
        "incident_resolved": "Incident Resolved",
        "incident_description": "Incident Description",
        "actions_taken": "Actions Taken",
        "submit_incident": "Submit Incident",
        "description_required": "Description is required",
        "incident_submitted": "Incident submitted successfully",
        "no_submissions_yet": "No submissions yet",
        
        # Visitor Interface
        "check_in": "Check-in",
        "sop_guidelines": "SOP Guidelines",
        "visitor_log": "Visitor Log",
        "visitor_registration": "Visitor Registration",
        "full_name": "Full Name",
        "company_organization": "Company/Organization",
        "phone_number": "Phone Number",
        "purpose_of_visit": "Purpose of Visit",
        "acknowledgments": "Acknowledgments",
        "health_declaration": "Health Declaration",
        "biosecurity_agreement": "Biosecurity Agreement",
        "sop_agreement": "SOP Agreement",
        "register_visit": "Register Visit",
        "fill_required_fields": "Please fill all required fields",
        "accept_all_agreements": "Please accept all agreements",
        "registration_successful": "Registration successful!",
        "access_restricted": "Access restricted to authorized personnel only",
        "no_visitors_logged": "No visitors logged",
        "download_csv": "Download CSV",
        
        # Analytics
        "analytics_dashboard": "Analytics Dashboard",
        "start_date": "Start Date",
        "end_date": "End Date",
        "risk_analysis": "Risk Analysis",
        "mortality_trends": "Mortality Trends",
        "hygiene_scores": "Hygiene Scores",
        "incident_reports": "Incident Reports",
        "compliance_report": "Compliance Report",
        "hygiene_analysis": "Hygiene Analysis",
        "incident_analysis": "Incident Analysis",
        
        # General
        "access_denied": "Access denied. Insufficient permissions.",
        "no_data_available": "No data available",
        "error_occurred": "An error occurred",
        "success": "Success",
        "loading": "Loading...",
    },
    
    "es": {
        # Autenticación
        "login_title": "FarmTwin 360 - Iniciar Sesión",
        "demo_users": "Usuarios Demo",
        "email": "Correo Electrónico",
        "password": "Contraseña",
        "login": "Iniciar Sesión",
        "logout": "Cerrar Sesión",
        "login_success": "¡Inicio de sesión exitoso!",
        "login_error": "Correo o contraseña inválidos",
        "welcome": "Bienvenido",
        "role": "Rol",
        
        # Navegación
        "navigation": "Navegación",
        "dashboard": "Panel Principal",
        "admin_panel": "Panel de Administrador",
        "worker_interface": "Interfaz de Trabajador",
        "visitor_check_in": "Registro de Visitantes",
        "analytics": "Análisis",
        
        # Panel Principal
        "total_barns": "Total de Granjas",
        "high_risk_barns": "Granjas de Alto Riesgo",
        "total_checklists": "Total de Listas de Verificación",
        "unresolved_incidents": "Incidentes Sin Resolver",
        "farm_visualization": "Visualización de Granja",
        "recent_activities": "Actividades Recientes",
        "risk_distribution": "Distribución de Riesgo",
        "checklist_trends": "Tendencias de Listas",
        "update_ai_predictions": "Actualizar Predicciones IA",
        "updating_predictions": "Actualizando predicciones IA...",
        "predictions_updated": "¡Predicciones IA actualizadas exitosamente!",
        "predictions_error": "Error al actualizar predicciones",
        
        # Panel de Administrador
        "user_management": "Gestión de Usuarios",
        "farm_management": "Gestión de Granjas",
        "system_settings": "Configuración del Sistema",
        "add_new_user": "Agregar Nuevo Usuario",
        "existing_users": "Usuarios Existentes",
        "user_actions": "Acciones de Usuario",
        "deactivate_user": "Desactivar Usuario",
        "activate_user": "Activar Usuario",
        "deactivate": "Desactivar",
        "activate": "Activar",
        "user_deactivated": "Usuario desactivado exitosamente",
        "user_activated": "Usuario activado exitosamente",
        "no_users_found": "No se encontraron usuarios",
        "name": "Nombre",
        "create_user": "Crear Usuario",
        "fill_all_fields": "Por favor complete todos los campos requeridos",
        "invalid_email": "Formato de correo inválido",
        "add_new_farm": "Agregar Nueva Granja",
        "existing_farms": "Granjas Existentes",
        "farm_name": "Nombre de Granja",
        "location": "Ubicación",
        "description": "Descripción",
        "create_farm": "Crear Granja",
        "farm_name_required": "El nombre de la granja es requerido",
        "farm_created": "Granja creada exitosamente",
        "farm_creation_error": "Error al crear la granja",
        "no_farms_found": "No se encontraron granjas",
        
        # Interfaz de Trabajador
        "submit_checklist": "Enviar Lista de Verificación",
        "report_incident": "Reportar Incidente",
        "my_submissions": "Mis Envíos",
        "daily_checklist": "Lista de Verificación Diaria",
        "select_barn": "Seleccionar Granja",
        "no_barns_available": "No hay granjas disponibles",
        "hygiene_score": "Puntuación de Higiene (1-10)",
        "mortality_count": "Conteo de Mortalidad",
        "feed_quality": "Calidad del Alimento (1-10)",
        "water_quality": "Calidad del Agua (1-10)",
        "ventilation_score": "Puntuación de Ventilación (1-10)",
        "temperature_celsius": "Temperatura (°C)",
        "humidity_percentage": "Humedad (%)",
        "location_data": "Datos de Ubicación",
        "latitude": "Latitud",
        "longitude": "Longitud",
        "notes": "Notas",
        "upload_photo": "Subir Foto",
        "incident_report": "Reporte de Incidente",
        "incident_type": "Tipo de Incidente",
        "severity": "Severidad",
        "incident_resolved": "Incidente Resuelto",
        "incident_description": "Descripción del Incidente",
        "actions_taken": "Acciones Tomadas",
        "submit_incident": "Enviar Incidente",
        "description_required": "La descripción es requerida",
        "incident_submitted": "Incidente enviado exitosamente",
        "no_submissions_yet": "Aún no hay envíos",
        
        # Interfaz de Visitantes
        "check_in": "Registro",
        "sop_guidelines": "Guías SOP",
        "visitor_log": "Registro de Visitantes",
        "visitor_registration": "Registro de Visitante",
        "full_name": "Nombre Completo",
        "company_organization": "Empresa/Organización",
        "phone_number": "Número de Teléfono",
        "purpose_of_visit": "Propósito de la Visita",
        "acknowledgments": "Reconocimientos",
        "health_declaration": "Declaración de Salud",
        "biosecurity_agreement": "Acuerdo de Bioseguridad",
        "sop_agreement": "Acuerdo SOP",
        "register_visit": "Registrar Visita",
        "fill_required_fields": "Por favor complete todos los campos requeridos",
        "accept_all_agreements": "Por favor acepte todos los acuerdos",
        "registration_successful": "¡Registro exitoso!",
        "access_restricted": "Acceso restringido solo a personal autorizado",
        "no_visitors_logged": "No hay visitantes registrados",
        "download_csv": "Descargar CSV",
        
        # Análisis
        "analytics_dashboard": "Panel de Análisis",
        "start_date": "Fecha de Inicio",
        "end_date": "Fecha de Fin",
        "risk_analysis": "Análisis de Riesgo",
        "mortality_trends": "Tendencias de Mortalidad",
        "hygiene_scores": "Puntuaciones de Higiene",
        "incident_reports": "Reportes de Incidentes",
        "compliance_report": "Reporte de Cumplimiento",
        "hygiene_analysis": "Análisis de Higiene",
        "incident_analysis": "Análisis de Incidentes",
        
        # General
        "access_denied": "Acceso denegado. Permisos insuficientes.",
        "no_data_available": "No hay datos disponibles",
        "error_occurred": "Ocurrió un error",
        "success": "Éxito",
        "loading": "Cargando...",
    }
}

# Current language (default to English)
if "language" not in st.session_state:
    st.session_state.language = "en"

def set_language(lang_code):
    """Set the current language"""
    if lang_code in translations:
        st.session_state.language = lang_code

def get_text(key):
    """Get translated text for the given key"""
    lang = st.session_state.get("language", "en")
    return translations.get(lang, {}).get(key, translations["en"].get(key, key))

def get_current_language():
    """Get current language code"""
    return st.session_state.get("language", "en")
