/*************************************************************************/
/*  image_loader_avif.h                                                  */
/*************************************************************************/
/* Copyright (c) 2020-2022 Fabio Alessandrell, Maffle LLC.               */
/*                                                                       */
/* Permission is hereby granted, free of charge, to any person obtaining */
/* a copy of this software and associated documentation files (the       */
/* "Software"), to deal in the Software without restriction, including   */
/* without limitation the rights to use, copy, modify, merge, publish,   */
/* distribute, sublicense, and/or sell copies of the Software, and to    */
/* permit persons to whom the Software is furnished to do so, subject to */
/* the following conditions:                                             */
/*                                                                       */
/* The above copyright notice and this permission notice shall be        */
/* included in all copies or substantial portions of the Software.       */
/*                                                                       */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,       */
/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF    */
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.*/
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY  */
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,  */
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE     */
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                */
/*************************************************************************/

#ifndef IMAGE_LOADER_AVIF_H
#define IMAGE_LOADER_AVIF_H

#include "godot_cpp/classes/file.hpp"
#include "godot_cpp/classes/image.hpp"
#include "godot_cpp/classes/image_format_loader.hpp"

#include <avif/avif.h>

class ImageLoaderAVIF : public godot::ImageFormatLoader {
	GDCLASS(ImageLoaderAVIF, godot::ImageFormatLoader);

protected:
	static void _bind_methods() {}

	static godot::Error avif_load_image_from_buffer(godot::Image *p_image, const uint8_t *p_buffer, int p_buffer_len, avifDecoder *p_decoder);
	static godot::Ref<godot::Image> _avif_mem_loader_func(const uint8_t *p_buffer, int p_size);

public:
	virtual int64_t _load_image(const godot::Ref<godot::Image> &p_image, const godot::String &p_path, bool p_force_linear, double p_scale) override;
	virtual godot::PackedStringArray _get_recognized_extensions() const override;
	ImageLoaderAVIF();
};

#endif
