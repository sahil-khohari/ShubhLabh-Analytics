import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { User, Building, CheckCircle2, Lock, Loader2, Save } from 'lucide-react';
import toast from 'react-hot-toast';

const presetCategories = ["Grocery", "Clothing", "Electronics", "Bakery", "Pharmacy", "Hardware", "Cosmetics", "Other"];

const Profile = () => {
    const [profile, setProfile] = useState({
        name: '',
        email: '',
        business_name: '',
        business_category: '',
        phone_number: '',
        store_address: ''
    });
    
    const [customCategory, setCustomCategory] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await api.get('/users/profile');
            const data = response.data;
            
            let categoryToSet = data.business_category || '';
            let customToSet = '';
            
            if (categoryToSet && categoryToSet !== 'Other' && !presetCategories.includes(categoryToSet)) {
                customToSet = categoryToSet;
                categoryToSet = 'Other';
            }
            
            setProfile({
                ...data,
                business_category: categoryToSet
            });
            setCustomCategory(customToSet);
            setIsLoading(false);
        } catch (error) {
            console.error('Error fetching profile:', error);
            toast.error('Failed to load profile data.');
            setIsLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        
        if (name === 'business_category' && value !== 'Other') {
            setCustomCategory('');
        }
        
        setProfile((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    const handleCustomCategoryChange = (e) => {
        setCustomCategory(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        
        try {
            const finalCategory = profile.business_category === 'Other' 
                ? customCategory.trim() 
                : profile.business_category;
                
            const updateData = {
                name: profile.name,
                business_name: profile.business_name,
                business_category: finalCategory,
                phone_number: profile.phone_number,
                store_address: profile.store_address
            };
            
            await api.put('/users/profile', updateData);
            toast.success('Profile updated successfully!');
        } catch (error) {
            console.error('Error updating profile:', error);
            toast.error('Failed to update profile.');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-canvas">
                <Loader2 className="w-8 h-8 animate-spin text-accent" />
            </div>
        );
    }

    const firstLetter = profile.name ? profile.name.charAt(0).toUpperCase() : 'U';

    return (
        <div className="p-8 max-w-5xl mx-auto space-y-6">
            {/* Page Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-slate-900">Profile & Business Settings</h1>
                <p className="text-slate-500 mt-2">Manage your account and business information</p>
            </div>

            {/* Profile Summary Card */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-full bg-sidebar flex items-center justify-center text-accent text-2xl font-bold shadow-sm">
                        {firstLetter}
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                            {profile.name}
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                        </h2>
                        <p className="text-slate-500">{profile.email}</p>
                    </div>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6 pb-12">
                {/* Personal Information */}
                <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2 pb-4 border-b border-slate-100">
                        <User className="w-5 h-5 text-accent" />
                        Personal Information
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="md:col-span-2">
                            <label className="block mb-2 text-slate-700 font-medium text-sm">Email Address (Read Only)</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-slate-400" />
                                </div>
                                <input
                                    type="email"
                                    value={profile.email}
                                    disabled
                                    className="w-full pl-10 p-3 rounded-lg border border-slate-200 bg-slate-50 text-slate-500 cursor-not-allowed focus:outline-none"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block mb-2 text-slate-700 font-medium text-sm">Owner Name *</label>
                            <input
                                type="text"
                                name="name"
                                value={profile.name}
                                onChange={handleChange}
                                required
                                className="w-full p-3 rounded-lg border border-slate-200 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-shadow"
                            />
                        </div>

                        <div>
                            <label className="block mb-2 text-slate-700 font-medium text-sm">Phone Number</label>
                            <input
                                type="tel"
                                name="phone_number"
                                value={profile.phone_number || ''}
                                onChange={handleChange}
                                placeholder="+1 234 567 8900"
                                className="w-full p-3 rounded-lg border border-slate-200 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-shadow"
                            />
                        </div>
                    </div>
                </div>

                {/* Business Information */}
                <div className="bg-white p-6 sm:p-8 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2 pb-4 border-b border-slate-100">
                        <Building className="w-5 h-5 text-accent" />
                        Business Information
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block mb-2 text-slate-700 font-medium text-sm">Business Name *</label>
                            <input
                                type="text"
                                name="business_name"
                                value={profile.business_name || ''}
                                onChange={handleChange}
                                required
                                placeholder="Enter your business name"
                                className="w-full p-3 rounded-lg border border-slate-200 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-shadow"
                            />
                        </div>

                        <div>
                            <label className="block mb-2 text-slate-700 font-medium text-sm">Business Category</label>
                            <select
                                name="business_category"
                                value={profile.business_category || ''}
                                onChange={handleChange}
                                className="w-full p-3 rounded-lg border border-slate-200 bg-white text-slate-900 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-shadow"
                            >
                                <option value="" disabled>Select a category</option>
                                {presetCategories.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                        </div>

                        {profile.business_category === 'Other' && (
                            <div className="md:col-span-2">
                                <label className="block mb-2 text-slate-700 font-medium text-sm">Specify Business Category</label>
                                <input
                                    type="text"
                                    value={customCategory}
                                    onChange={handleCustomCategoryChange}
                                    placeholder="Enter your business category"
                                    className="w-full p-3 rounded-lg border border-slate-200 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-shadow"
                                />
                            </div>
                        )}

                        <div className="md:col-span-2">
                            <label className="block mb-2 text-slate-700 font-medium text-sm">Store Address</label>
                            <textarea
                                name="store_address"
                                value={profile.store_address || ''}
                                onChange={handleChange}
                                placeholder="Full store address"
                                rows="3"
                                className="w-full p-3 rounded-lg border border-slate-200 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent resize-y transition-shadow"
                            ></textarea>
                        </div>
                    </div>
                </div>

                {/* Save Area */}
                <div className="flex flex-col sm:flex-row items-center justify-between p-6 bg-white rounded-xl shadow-sm border border-slate-200">
                    <p className="text-slate-500 text-sm mb-4 sm:mb-0">
                        Your changes will be securely saved to your account.
                    </p>
                    <div className="flex gap-4 w-full sm:w-auto">
                        <button 
                            type="submit" 
                            disabled={isSaving}
                            className="w-full sm:w-auto px-6 py-2.5 bg-accent text-sidebar rounded-lg font-bold hover:bg-yellow-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-sm"
                        >
                            {isSaving ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save className="w-5 h-5" />
                                    Save Changes
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default Profile;
